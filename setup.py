#!/usr/bin/env python3
"""
Setup script for RA9 - Ultra-Deep Cognitive Engine
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("ra9/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ra9_ai",
    version="0.1.0",
    author="RA9 Development Team",
    author_email="contact@ra9.ai",
    description="RA9 - Ultra-Deep Cognitive Engine with Multi-Agent Architecture",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ra9",
    packages=find_packages(), # Find all packages in the current directory
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ra9=ra9.main:main", # Correct entry point
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="ai, cognitive-engine, multi-agent, artificial-intelligence, cognitive-architecture",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ra9/issues",
        "Source": "https://github.com/yourusername/ra9",
        "Documentation": "https://github.com/yourusername/ra9#readme",
    },
)
