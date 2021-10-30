from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="masonite-billing",
    version='4.0.0',
    packages=[
        'masonite.billing',
        'masonite.billing.commands',
        'masonite.billing.contracts',
        'masonite.billing.controllers',
        'masonite.billing.drivers',
        'masonite.billing.factories',
        'masonite.billing.models',
    ],
    package_dir={"": "src"},
    description="The Masonite Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://github.com/masoniteframework/billing",
    # Author details
    author="Joe Mancuso",
    author_email="joe@masoniteproject.com",
    install_requires=[
        'masonite>=2.2',
        'cleo',
        'stripe==2.40.0',
    ],
    license="MIT",
    # If your package should include things you specify in your MANIFEST.in file
    # Use this option if your package needs to include files that are not python files
    # like html templates or css files
    include_package_data=True,
)
