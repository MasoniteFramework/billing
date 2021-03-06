''' Database Settings '''

import os

from dotenv import find_dotenv, load_dotenv
from orator import DatabaseManager, Model
from masonite import env

'''
|--------------------------------------------------------------------------
| Load Environment Variables
|--------------------------------------------------------------------------
|
| Loads in the environment variables when this page is imported.
|
'''

load_dotenv(find_dotenv())

'''
|--------------------------------------------------------------------------
| Database Settings
|--------------------------------------------------------------------------
|
| Set connection database settings here as a dictionary. Follow the
| format below to create additional connection settings.
|
| @see Orator migrations documentation for more info
|
'''
DATABASES = {
    'default': os.environ.get('DB_DRIVER'),
    'sqlite': {
        'driver': 'sqlite',
        'database': os.environ.get('DB_DATABASE')
    },
    os.environ.get('DB_DRIVER'): {
        'driver': os.environ.get('DB_DRIVER'),
        'database': os.environ.get('DB_DATABASE'),
        'prefix': ''
    }
}

DB = DatabaseManager(DATABASES)
Model.set_connection_resolver(DB)
