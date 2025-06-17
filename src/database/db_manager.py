"""
Database Manager for ClipForge
Handles SQLite database operations for storing processing history and cache
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseManager:
    """
    Manages SQLite database operations for ClipForge
    Stores processing history, transcriptions, and user preferences
    """
    
    def __init__(self, db_path: str = "clipforge.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Processing history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        file_size INTEGER,
                        duration REAL,
                        processing_time REAL,
                        features_used TEXT,  -- JSON array of features used
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'completed'
                    )
                """)
                
                # Transcription cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transcription_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_hash TEXT UNIQUE NOT NULL,
                        filename TEXT NOT NULL,
                        model_used TEXT NOT NULL,
                        transcript_data TEXT,  -- JSON of full transcript
                        captions_data TEXT,    -- JSON of captions array
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # User preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # App statistics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        videos_processed INTEGER DEFAULT 0,
                        total_processing_time REAL DEFAULT 0.0,
                        total_time_saved REAL DEFAULT 0.0,
                        features_usage TEXT,  -- JSON of feature usage counts
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def add_processing_record(self, filename: str, file_size: int, duration: float, 
                            processing_time: float, features_used: List[str]) -> int:
        """
        Add a processing record to history
        
        Args:
            filename: Name of processed file
            file_size: File size in bytes
            duration: Video duration in seconds
            processing_time: Time taken to process in seconds
            features_used: List of features used
            
        Returns:
            int: Record ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processing_history 
                    (filename, file_size, duration, processing_time, features_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (filename, file_size, duration, processing_time, json.dumps(features_used)))
                
                record_id = cursor.lastrowid
                conn.commit()
                
                # Update statistics
                self.update_statistics(processing_time, features_used)
                
                logger.info(f"Processing record added: {filename}")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to add processing record: {e}")
            raise
    
    def cache_transcription(self, file_hash: str, filename: str, model_used: str,
                          transcript_data: Dict, captions_data: List[Dict]) -> bool:
        """
        Cache transcription results
        
        Args:
            file_hash: Unique hash of the file
            filename: Original filename
            model_used: Whisper model used
            transcript_data: Full transcript data from Whisper
            captions_data: Processed captions array
            
        Returns:
            bool: Success status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO transcription_cache
                    (file_hash, filename, model_used, transcript_data, captions_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    file_hash, filename, model_used, 
                    json.dumps(transcript_data), 
                    json.dumps(captions_data)
                ))
                
                conn.commit()
                logger.info(f"Transcription cached: {filename}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cache transcription: {e}")
            return False
    
    def get_cached_transcription(self, file_hash: str, model_used: str) -> Optional[Dict]:
        """
        Retrieve cached transcription
        
        Args:
            file_hash: Unique hash of the file
            model_used: Whisper model used
            
        Returns:
            Dict or None: Cached transcription data
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT transcript_data, captions_data, created_at
                    FROM transcription_cache
                    WHERE file_hash = ? AND model_used = ?
                """, (file_hash, model_used))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'transcript': json.loads(row['transcript_data']),
                        'captions': json.loads(row['captions_data']),
                        'cached_at': row['created_at']
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve cached transcription: {e}")
            return None
    
    def get_processing_history(self, limit: int = 50) -> List[Dict]:
        """
        Get processing history records
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of processing records
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM processing_history
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                records = []
                
                for row in rows:
                    record = dict(row)
                    record['features_used'] = json.loads(record['features_used'])
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Failed to get processing history: {e}")
            return []
    
    def update_statistics(self, processing_time: float, features_used: List[str]):
        """
        Update app statistics
        
        Args:
            processing_time: Time taken for processing
            features_used: List of features used
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current statistics
                cursor.execute("SELECT * FROM app_statistics ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                
                if row:
                    # Update existing record
                    videos_processed = row['videos_processed'] + 1
                    total_time = row['total_processing_time'] + processing_time
                    
                    # Update feature usage
                    current_usage = json.loads(row['features_usage']) if row['features_usage'] else {}
                    for feature in features_used:
                        current_usage[feature] = current_usage.get(feature, 0) + 1
                    
                    cursor.execute("""
                        UPDATE app_statistics
                        SET videos_processed = ?, total_processing_time = ?, 
                            features_usage = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (videos_processed, total_time, json.dumps(current_usage), row['id']))
                    
                else:
                    # Create first record
                    feature_usage = {feature: 1 for feature in features_used}
                    cursor.execute("""
                        INSERT INTO app_statistics
                        (videos_processed, total_processing_time, features_usage)
                        VALUES (?, ?, ?)
                    """, (1, processing_time, json.dumps(feature_usage)))
                
                conn.commit()
                logger.info("Statistics updated")
                
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current app statistics
        
        Returns:
            Dict: Current statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM app_statistics ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                
                if row:
                    stats = dict(row)
                    stats['features_usage'] = json.loads(stats['features_usage']) if stats['features_usage'] else {}
                    return stats
                else:
                    return {
                        'videos_processed': 0,
                        'total_processing_time': 0.0,
                        'total_time_saved': 0.0,
                        'features_usage': {}
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def set_preference(self, key: str, value: str):
        """Set user preference"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences (key, value)
                    VALUES (?, ?)
                """, (key, value))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to set preference {key}: {e}")
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get user preference"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row['value'] if row else default
                
        except Exception as e:
            logger.error(f"Failed to get preference {key}: {e}")
            return default
    
    def cleanup_old_cache(self, days: int = 30):
        """
        Clean up old cached transcriptions
        
        Args:
            days: Number of days to keep cache
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM transcription_cache
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old cache entries")
                
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")

# Global database instance
db_manager = DatabaseManager() 