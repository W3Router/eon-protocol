
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eon-protocol",
    version="0.1.0",
    author="EON Team",
    author_email="team@eon-protocol.io",
    description="Privacy-preserving distributed computation protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eon-protocol/eon",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tenseal>=0.3.0",
        "numpy>=1.21.0",
        "grpcio>=1.44.0",
        "grpcio-tools>=1.44.0",
        "fastapi>=0.75.0",
        "uvicorn>=0.17.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "python-jose>=3.3.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eon=eon.cli:main",
        ],
    },
)
