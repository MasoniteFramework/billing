import os
import pytest

from dotenv import find_dotenv, load_dotenv
from billing.models.Billable import Billable
from billing.exceptions import PlanNotFound
from masonite.app import App

load_dotenv(find_dotenv())


class User(Billable):
    pass

user = User()
user.customer_id = user.create_customer('test-customer', 'tok_amex')


def test_subscription_raises_exeption():
    with pytest.raises(PlanNotFound):
        user.subscribe('default', 'no-plan', 'tok_amex')

def test_subscription_subscribes_user():
    subscription = user.subscribe('default', 'masonite-test', 'tok_amex')
    assert subscription.startswith('sub')
    user.plan_id = subscription
    user.cancel()
    

def test_is_subscribed():
    subscription = user.subscribe('default', 'masonite-test', 'tok_amex')
    user.plan_id = subscription

    assert user.is_subscribed() is True
    assert user.is_subscribed('masonite-test') is True
    assert user.cancel()
    assert user.is_subscribed('masonite-test') is False
    assert user.is_subscribed() is False

    wrong_token_user = User()
    wrong_token_user.customer_id = 'incorrect_token'
    assert wrong_token_user.is_subscribed() is False

def test_cancel_billing():
    subscription = user.subscribe('default', 'masonite-flash', 'tok_amex')
    user.plan_id = subscription
    
    assert user.is_subscribed('masonite-flash') is True
    assert user.cancel() is True
    assert user.is_subscribed('masonite-flash') is False
    assert user.is_subscribed() is False

def test_on_trial():
    subscription = user.subscribe('default', 'masonite-flash', 'tok_amex')
    user.plan_id = subscription
    assert user.on_trial() is False
    assert user.cancel() is True

    subscription = user.trial(days=7).subscribe('default', 'masonite-flash', 'tok_amex')
    user.plan_id = subscription
    assert user.on_trial() is True
    assert user.cancel() is True
