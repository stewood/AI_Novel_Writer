from setuptools import setup, find_packages

setup(
    name="novelwriter_idea",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0.0",
        "python-slugify>=8.0.0",
        "rich>=13.0.0",  # For better console output
        "openai>=1.0.0",  # For OpenRouter integration
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "novelwriter_idea=novelwriter_idea.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for generating novel ideas using AI agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="novel writing, AI, creative writing, story generation",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Writers",
        "Topic :: Text Processing :: General",
    ],
) 