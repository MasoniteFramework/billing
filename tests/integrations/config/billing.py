import os


DRIVERS = {
    "default": "stripe",
    "stripe": {
        "client": os.getenv("STRIPE_CLIENT"),
        "secret": os.getenv("STRIPE_SECRET"),
        "currency": "usd",
    },
}
