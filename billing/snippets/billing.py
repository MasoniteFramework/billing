''' Masonite Billing Settings '''

import os

DRIVER = 'stripe'

DRIVERS = {
    'stripe': {
        'client': os.getenv('STRIPE_CLIENT'),
        'secret': os.getenv('STRIPE_SECRET'),
        'currency': 'usd',
    }
}