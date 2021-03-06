import os
import pytest
import time

from dotenv import find_dotenv, load_dotenv
from billing.models import Billable, Subscription
from billing.exceptions import PlanNotFound
from masonite.app import App
import pendulum

load_dotenv(find_dotenv())

class User(Billable):
    plan_id = None
    id = 1
    def save(self):
        pass

user = User()
user.email = "test@email.com"

if os.environ.get('STRIPE_CUSTOMER'):
    user.customer_id = os.getenv('STRIPE_CUSTOMER')
else:
    user.customer_id = user.create_customer('test-customer', 'tok_amex')

# ensure there is a card on the account
user.card('tok_amex')

def test_subscription_raises_exeption():
    with pytest.raises(PlanNotFound):
        user.subscribe('no-plan', 'tok_amex')

def test_subscription_subscribes_user():
    user.subscribe('masonite-test', 'tok_amex')
    assert user.plan_id.startswith('sub')
    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)


def test_is_subscribed():
    user.subscribe('masonite-test', 'tok_amex')

    assert user.is_subscribed() is True
    assert user.is_subscribed('masonite-test') is True
    assert user.is_canceled() is False
    assert user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)

    assert user.is_subscribed('masonite-test') is False
    assert user.is_subscribed() is False

    wrong_token_user = User()
    wrong_token_user.plan_id = 'incorrect_token'
    assert wrong_token_user.is_subscribed() is False


def test_cancel_billing():
    user.subscribe('masonite-flash', 'tok_amex')
    
    assert user.is_subscribed('masonite-flash') is True
    assert user.cancel(now=True) is True
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)

    assert user.is_subscribed('masonite-flash') is False
    assert user.is_subscribed() is False


def test_on_trial():
    user.subscribe('masonite-flash', 'tok_amex')
    assert user.on_trial() is False
    assert user.cancel(now=True) is True
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)


    user.trial(days=7).subscribe('masonite-flash', 'tok_amex')
    assert user.on_trial() is True
    assert user.cancel(now=False) is True
    assert user.on_trial() is True
    assert user.cancel(now=True) is True
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)

    assert user.on_trial() is False


def test_subscribe_cancel_subscription_at_end_of_period():
    user.subscribe('masonite-flash', 'tok_amex')

    assert user.is_subscribed() is True
    user.cancel(now=False)
    assert user.is_subscribed() is True
    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)

    assert user.is_subscribed() is False


def test_subscription_is_canceled():
    user.subscribe('masonite-flash', 'tok_amex')
    
    assert user.is_canceled() == False
    user.cancel(now=False)
    assert user.is_canceled() == True

    user.cancel(now=True)
    assert user.is_canceled() == False


def test_skip_trial():
    user.subscribe('masonite-test', 'tok_amex')

    assert user.on_trial() is True
    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)


    user.skip_trial().subscribe('masonite-test', 'tok_amex')

    assert user.on_trial() is False
    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)



def test_charge_customer():
    user.email = 'test@email.com'
    assert user.charge(999) is True
    assert user.charge(999, token='tok_amex')
    assert user.charge(299, metadata={'name': 'test'})
    assert user.charge(299, description='Charge For test@email.com')


def test_swap_plan():
    user.subscribe('masonite-test', 'tok_amex')

    assert user.is_subscribed('masonite-test')
    assert user.swap('masonite-flash') is True
    assert user.is_subscribed() is True
    assert user.is_subscribed('masonite-flash') is True
    assert user.is_subscribed('masonite-test') is False

    assert user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)



def test_change_card():
    assert user.card('tok_amex') is True


def test_cancel_and_resume_plan():
    user.skip_trial().subscribe('masonite-test', 'tok_amex')

    # assert user.is_canceled() is False
    assert user.cancel() is True
    assert user.is_canceled() is True
    assert user.resume()
    assert user.is_canceled() is False

    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)



def test_plan_returns_plan_name():
    user.skip_trial().subscribe('masonite-test', 'tok_amex')

    assert user.plan() == 'Masonite Test'

    assert user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)



def test_is_on_trial_after_trial():
    user.subscribe('masonite-test', 'tok_amex')
    assert user.on_trial()

    # set the trial to an expired time
    subscription = user._get_subscription()
    subscription.trial_ends_at = pendulum.now().subtract(days=1)
    subscription.save()

    assert user.on_trial() is False
    assert user.on_trial() is False

    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)



def test_subscription_is_over():
    user.skip_trial().subscribe('masonite-test', 'tok_amex')
    assert user.is_subscribed() is True
    assert user.on_trial() is False

    # set the subscription to an expired time
    subscription = user._get_subscription()
    subscription.ends_at = pendulum.now().subtract(minutes=1)
    subscription.save()

    assert user.on_trial() is False

    assert user.was_subscribed() is True
    assert user.was_subscribed('masonite-test') is True
    assert user.was_subscribed('masonite-flash') is False

    assert user.is_subscribed() is False

    user.cancel(now=True)
    if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        time.sleep(2)

def test_can_use_coupon_on_charge():
    assert user._processor._apply_coupon(1000) == 1000
    assert user.coupon('5-off')._processor._apply_coupon(500) == 400
    assert user.coupon('10-percent-off')._processor._apply_coupon(1000) == 900
    assert user.coupon('10-percent-off')._processor._apply_coupon(1499) == 1349.1
    assert user.coupon(.10)._processor._apply_coupon(1499) == 1349.1
    assert user.coupon(100)._processor._apply_coupon(1000) == 900


def test_can_use_coupon_on_subscription():
    user.skip_trial().coupon('5-off').subscribe('masonite-test', 'tok_amex')
    assert user.is_subscribed() is True
    assert user.on_trial() is False
    subscription = user._get_subscription()

    user.cancel(now=True)

