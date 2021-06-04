#!/usr/bin/env python
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="centraldogma",
    version="0.1.0",
    packages=["centraldogma", "centraldogma.data"],
    description="Central Dogma client in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/line/centraldogma-python",
    author="",
    license="MIT",
    author_email="",
    install_requires=["requests", "marshmallow", "dataclasses-json"],
    keywords="centraldogma",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
