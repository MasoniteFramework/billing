from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="masonite-billing",
    version="4.0.0",
    packages=[
        "masonite.billing",
        "masonite.billing.commands",
        "masonite.billing.config",
        "masonite.billing.controllers",
        "masonite.billing.drivers",
        "masonite.billing.models",
        "masonite.billing.providers",
    ],
    package_dir={"": "src"},
    description="Masonite billing management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://github.com/masoniteframework/billing",
    # Author details
    author="Joe Mancuso",
    author_email="joe@masoniteproject.com",
    install_requires=[
        "masonite>=4.0<5.0",
        "cleo",
        "stripe==2.40.0",
    ],
    license="MIT",
    keywords="Masonite, Python, Stripe",
    # If your package should include things you specify in your MANIFEST.in file
    # Use this option if your package needs to include files that are not python files
    # like html templates or css files
    include_package_data=True,
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # $ pip install your-package[dev,test]
    extras_require={
        "test": [
            "coverage",
            "pytest",
            "pytest-cov",
            "coveralls",
        ],
        "dev": [
            "black",
            "flake8",
            "twine>=1.5.0",
        ],
    },
)
