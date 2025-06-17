"""
Setup script for ClipForge AI Video Editor
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clipforge",
    version="0.1.0",
    author="ClipForge Team",
    author_email="contact@clipforge.ai",
    description="AI-powered video editor with automatic captions, B-roll, and meme effects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noahwilliamshaffer/AiVideoEditor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Content Creators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
            "pre-commit>=3.0",
        ],
        "gpu": [
            "torch[cuda]>=2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "clipforge=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
) 