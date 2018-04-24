""" A InstallCommand Command """
import os

from cleo import Command
from masonite.packages import create_or_append_config

package_directory = os.path.dirname(os.path.realpath(__file__))

class InstallCommand(Command):
    """
    Install Masonite Billing

    install:billing
    """

    def handle(self):
        create_or_append_config(
            os.path.join(
                package_directory,
                '../snippets/billing.py'
            )
        )
