from setuptools import setup, find_packages


def get_requirements(filename):
    """Get requirements from requirements.txt"""
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="pypsa-dashboard",
    version="1.0",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)
