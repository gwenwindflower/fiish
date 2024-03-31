from setuptools import find_packages, setup


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


requirements = parse_requirements("requirements.in")
setup(
    name="fish",
    version="0.1",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    package_dir={"fish": "fish"},
    entry_points={"console_scripts": ["fish = fish.cli:cli"]},
    install_requires=requirements,
)
