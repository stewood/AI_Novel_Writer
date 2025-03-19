"""
Setup configuration for the Novel Writer package.

This setup script configures the package for installation, defining dependencies,
entry points, and package metadata.
"""

from setuptools import setup, find_packages

setup(
    name="novel_writer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0.0",
        "python-slugify>=8.0.0",
        "rich>=10.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "novel_writer=novel_writer.cli:cli",
        ],
    },
    python_requires=">=3.8",
    author="Stephen Woodard",
    author_email="stewood@outlook.com",
    description="An AI-powered novel writing assistant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="novel writing, AI, creative writing, story generation, writing assistant",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    url="https://github.com/stewood/AI_Novel_Writer",
    project_urls={
        "Bug Tracker": "https://github.com/stewood/AI_Novel_Writer/issues",
        "Documentation": "https://github.com/stewood/AI_Novel_Writer/blob/main/README.md",
        "Source Code": "https://github.com/stewood/AI_Novel_Writer",
    },
) 