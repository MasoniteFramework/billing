import os
import pytest

from dotenv import find_dotenv, load_dotenv
from billing.models.Billable import Billable
from billing.exceptions import PlanNotFound
from masonite.app import App

load_dotenv(find_dotenv())



class User(Billable):
    pass

def test_subscription_raises_exeption():
    user = User()

    with pytest.raises(PlanNotFound):
        user.subscribe('default', 'no-plan', 'tok_amex')

def test_subscription_subscribes_user():
    user = User()
    subscription = user.subscribe('default', 'masonite-test', 'tok_amex')
    assert subscription.startswith('sub')

def test_is_subscribed():
    user = User()
    subscription = user.subscribe('default', 'masonite-test', 'tok_amex')
    # TODO

