#!/usr/bin/env python

from setuptools import setup

setup(
    name="taskschedule",
    version="0.1.0",
    license="MIT",
    author="Nicole Nisters",
    author_email="n.nisters@pm.me",
    description="A taskwarrior extension to display scheduled tasks.",
    long_description="A taskwarrior extension to display scheduled tasks."
    "It uses curses to show a table with scheduled tasks. "
    "The table is refreshed automatically.",
    url="https://github.com/nnist/taskschedule",
    classifiers=[
        "Environment :: Console :: Curses",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
    ],
    python_requires=">=3.5",
    packages=["taskschedule", "tests"],
    scripts=["scripts/taskschedule"],
    include_package_data=True,
    install_requires=["tasklib", "isodate"],
    extras_require={"dev": ["black", "flake8"]},
)
