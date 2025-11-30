from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="comptext-codex",
    version="3.5.0",
    author="ProfRandom92",
    author_email="your.email@example.com",
    description="A Domain-Specific Language for efficient LLM control with 70% token reduction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProfRandom92/comptext-codex",
    project_urls={
        "Bug Tracker": "https://github.com/ProfRandom92/comptext-codex/issues",
        "Documentation": "https://github.com/ProfRandom92/comptext-codex/blob/main/README.md",
        "Source Code": "https://github.com/ProfRandom92/comptext-codex",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "comptext=comptext.cli:main",
        ],
    },
    include_package_data=True,
    keywords="llm dsl prompts ai language-model mcp efficiency tokens",
    zip_safe=False,
)
