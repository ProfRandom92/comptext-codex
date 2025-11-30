#!/usr/bin/env python
"""Setup script for CompText-Codex."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="comptext-codex",
    version="3.5.0",
    author="CompText Team",
    description="A Domain-Specific Language for efficient LLM interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProfRandom92/comptext-codex",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "mcp": [
            "mcp>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "comptext=comptext_codex.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "comptext_codex": ["data/*.csv"],
    },
)
