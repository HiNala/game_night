from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flying-squirrel-simulator",
    version="1.0.0",
    author="Flying Squirrel Team",
    author_email="team@flyingsquirrel.game",
    description="A 3D flight simulator game featuring a flying squirrel with realistic gliding physics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HiNala/game_night",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Simulation",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flying-squirrel=game:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
) 