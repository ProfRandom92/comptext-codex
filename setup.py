#!/usr/bin/env python
"""Setup script for CompText-Codex."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="comptext-codex",
    version="5.0.0",
    author="CompText Team",
    description="CompText V5.0 ULTRA - 94% Token Reduction Protocol for LLM Communication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProfRandom92/comptext-codex",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
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
        "docs": [
            "mkdocs-material>=9.5.0",
            "mkdocs-minify-plugin>=0.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "comptext=comptext_codex.cli_v5:main",
            "comptext-v4=comptext_codex.cli:main",
            "comptext-mcp=comptext_codex.mcp_server_v5:main",
        ],
    },
)
