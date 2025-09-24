#!/usr/bin/env python3
"""Setup script for A2A Python SDK."""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback to hardcoded requirements if file not found
    requirements = [
        "requests>=2.31.0",
        "PyYAML>=6.0",
        'dataclasses>=0.6; python_version<"3.7"',
    ]

setup(
    name="a2a-reg-sdk",
    version="1.0.0",
    author="A2A Registry Team",
    author_email="team@a2areg.dev",
    description="Python SDK for the A2A Agent Registry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a2areg/a2a-registry",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    keywords="a2a, agents, ai, registry, sdk, python",
    project_urls={
        "Bug Reports": "https://github.com/a2areg/a2a-registry/issues",
        "Source": "https://github.com/a2areg/a2a-registry",
        "Documentation": "https://docs.a2areg.dev",
    },
)
