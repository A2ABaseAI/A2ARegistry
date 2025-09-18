#!/usr/bin/env python3
"""Setup script for A2A Publisher CLI tool."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="a2a-publisher",
    version="1.0.0",
    author="A2A Registry Team",
    author_email="team@a2areg.dev",
    description="CLI tool for publishing agents to the A2A Agent Registry",
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
    entry_points={
        "console_scripts": [
            "a2a-publisher=main:main",
        ],
    },
    keywords="a2a, agents, ai, registry, publisher, cli",
    project_urls={
        "Bug Reports": "https://github.com/a2areg/a2a-registry/issues",
        "Source": "https://github.com/a2areg/a2a-registry",
        "Documentation": "https://docs.a2areg.dev",
    },
)
