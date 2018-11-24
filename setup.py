from setuptools import setup


setup(
    name="masonite-billing",
    version='0.1.3',
    packages=[
        'billing',
        'billing.commands',
        'billing.drivers',
        'billing.managers',
        'billing.models',
        'billing.snippets',
        'billing.controllers',
    ],
    install_requires=[
        'masonite',
        'cleo',
        'stripe',
    ],
    include_package_data=True,
)
