from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name="enosimulator",
    version="0.0.1",
    description="Simulating an attack defense CTF competition using the game engine and services provided by Enowars",
    author="Jannik Novak",
    author_email="nevisha@pm.me",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashiven/enosimulator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "enosimulator = enosimulator.__main__:main",
        ],
    },
)
