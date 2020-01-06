from setuptools import setup


setup(
    name="masonite-billing",
    version='3.0.0b5',
    packages=[
        'billing',
        'billing.commands',
        'billing.contracts',
        'billing.controllers',
        'billing.drivers',
        'billing.factories',
        'billing.models',
        'billing.snippets',
    ],
    install_requires=[
        'masonite>=2.2',
        'cleo',
        'stripe==2.40.0',
    ],
    include_package_data=True,
)
