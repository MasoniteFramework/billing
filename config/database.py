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
    'default': 'mysql',
    'mysql': {
        'driver': 'mysql',
        'host': env('DB_HOST'),
        'database': env('DB_DATABASE'),
        'port': env('DB_PORT'),
        'user': env('DB_USERNAME'),
        'password': env('DB_PASSWORD'),
        'log_queries': env('DB_LOG'),
    },
}

DB = DatabaseManager(DATABASES)
Model.set_connection_resolver(DB)
