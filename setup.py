#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for Rich Color Log package.
"""

from setuptools import setup, find_packages
import os
import shutil
from pathlib import Path
import traceback

NAME = "richcolorlog"
this_directory = os.path.abspath(os.path.dirname(__file__))

if (Path(__file__).parent / '__version__.py').is_file():
    shutil.copy(str((Path(__file__).parent / '__version__.py')), os.path.join(this_directory, NAME, '__version__.py'))

if (Path(__file__).parent / 'screenshot.png').is_file():
    shutil.copy(str((Path(__file__).parent / 'screenshot.png')), os.path.join(this_directory, NAME, 'screenshot.png'))
    
# Read the contents of README file
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from __init__.py
def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "0.0.0"

print(f"NAME   : {NAME}")
print(f"VERSION: {get_version()}")

setup(
    name=NAME,
    version=get_version(),
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    description="Beautiful, powerful logging with Rich, emoji icons, syntax highlighting, and multi-output support (console, file, RabbitMQ, Kafka, DB, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/cumulus13/{NAME}",
    project_urls={
        "Bug Reports": "https://github.com/cumulus13/richcolorlog/issues",
        "Source": "https://github.com/cumulus13/richcolorlog",
    },
    # packages=find_packages(),
    packages=[NAME],
    py_modules=["richcolorlog"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    keywords="logging, rich, color, emoji, syntax-highlighting, rabbitmq, kafka, syslog, database",
    python_requires=">=3.8",
    install_requires=[
        "rich>=10.0.0",
    ],
    extras_require={
        "rabbitmq": ["pika>=1.0.0"],
        "kafka": ["kafka-python>=2.0.0"],
        "zmq": ["pyzmq>=20.0.0"],
        "db": [
            "psycopg2-binary>=2.8.0; sys_platform != 'win32'",
            "mysql-connector-python>=8.0.0",
            "sqlite3; python_version >= '3.8'",  # built-in, tapi disebut untuk kejelasan
        ],
        "all": [
            "pika>=1.0.0",
            "kafka-python>=2.0.0",
            "pyzmq>=20.0.0",
            "psycopg2-binary>=2.8.0; sys_platform != 'win32'",
            "mysql-connector-python>=8.0.0",
        ],
    },
    entry_points = {
        "console_scripts":
            [
                "richcolorlog = richcolorlog.__main__:main",
            ]
    },
    keywords="logging rich console terminal colors formatting",
    project_urls={
        "Bug Reports": f"https://github.com/cumulus13/{NAME}/issues",
        "Source": f"https://github.com/cumulus13/{NAME}",
        "Documentation": f"https://github.com/cumulus13/{NAME}#readme",
    },
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)