#!/usr/bin/env python
from pathlib import Path
from setuptools import find_packages, setup

HERE = Path(__file__).parent

version = (HERE / "airflow_code_editor" / "VERSION").read_text().strip()
long_description = (HERE / "README.md").read_text()
install_requires = (HERE / "requirements.txt").read_text().split("\n")

setup(
    name="airflow_code_editor",
    version=version,
    packages=find_packages(exclude=["scripts", "scripts.*", "tests", "tests.*"]),
    include_package_data=True,
    entry_points={
        "airflow.plugins": [
            "airflow_code_editor = airflow_code_editor.airflow_code_editor:CodeEditorPlugin"
        ]
    },
    zip_safe=False,
    url="https://github.com/andreax79/airflow-code-editor",
    author="Andrea Bonomi",
    author_email="andrea.bonomi@gmail.com",
    description="Apache Airflow code editor and file manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    license="Apache License, Version 2.0",
    python_requires=">=3.5",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    test_suite='tests',
    tests_require=['pytest'],
)
