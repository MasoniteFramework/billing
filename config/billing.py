''' Masonite Billing Settings '''

import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DRIVER = 'stripe'

DRIVERS = {
    'stripe': {
        'client': os.getenv('STRIPE_CLIENT'),
        'secret': os.getenv('STRIPE_SECRET'),
        'currency': 'usd',
    }
}