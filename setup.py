import os
from setuptools import setup

package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.md")
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
    author_email="",
    license="Apache 2.0",
    install_requires=["requests", "marshmallow", "dataclasses-json"],
    python_requires=">=3.7",
    keywords="centraldogma",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
