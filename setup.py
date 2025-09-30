# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.util import convert_path


_package_name = "beans_logging"

_namespace_dict = {}
_version_path = convert_path(f"{_package_name}/__version__.py")
with open(_version_path) as _version_file:
    exec(_version_file.read(), _namespace_dict)
_package_version = _namespace_dict["__version__"]

setup(
    name=_package_name,
    packages=find_packages(),
    version=f"{_package_version}",
    license="MIT",
    description=f"'{_package_name}' is a python package for simple logger and easily managing logging modules. It is a Loguru based custom logging package for python projects.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Batkhuu Byambajav",
    author_email="batkhuu10@gmail.com",
    url="https://github.com/bybatkhuu/module-python-logging",
    download_url=f"https://github.com/bybatkhuu/module-python-logging/archive/v{_package_version}.tar.gz",
    keywords=[
        _package_name,
        "loguru",
        "logging",
        "logger",
        "logs",
        "log",
        "print",
        "custom-logging",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0,<7.0",
        "pydantic>=1.10.0,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0",
        "loguru>=0.7.2,<1.0.0",
    ],
    extras_require={"fastapi": ["beans-logging-fastapi>=1.0.0,<2.0.0"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
