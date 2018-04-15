from setuptools import setup


setup(
    name="masonite-billing",
    version='0.0.1',
    packages=[
        'billing',
    ],
    install_requires=[
        'masonite',
    ],
    include_package_data=True,
)
