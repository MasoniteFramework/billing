from setuptools import setup


setup(
    name="masonite-billing",
    version='2.2.1',
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
        'stripe',
    ],
    include_package_data=True,
)
