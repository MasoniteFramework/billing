import os
import time
import pendulum

from masonite.tests import TestCase
from masonite.environment import env

from src.masonite.billing import Billable
from src.masonite.billing.exceptions import PlanNotFound


class User(Billable):
    plan_id = None
    id = 1

    def save(self):
        pass


class TestStripe(TestCase):
    @classmethod
    def setUpClass(cls):
        "Hook method for setting up class fixture before running tests in the class."
        cls.user = User()
        cls.user.email = "test@email.com"
        if env("STRIPE_CUSTOMER"):
            cls.user.customer_id = env("STRIPE_CUSTOMER")
        else:
            cls.user.customer_id = cls.user.create_customer("test-customer", "tok_amex")

        # ensure there is a card on the account
        cls.user.card("tok_amex")

    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
        pass

    def test_subscription_raises_exeption(self):
        with self.assertRaises(PlanNotFound):
            self.user.subscribe("no-plan", "tok_amex")

    def test_subscription_subscribes_user(self):
        self.user.subscribe("masonite-test", "tok_amex")
        assert self.user.plan_id.startswith("sub")
        self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

    def test_is_subscribed(self):
        self.user.subscribe("masonite-test", "tok_amex")

        assert self.user.is_subscribed()
        assert self.user.is_subscribed("masonite-test")
        assert not self.user.is_canceled()
        assert self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

        assert not self.user.is_subscribed("masonite-test")
        assert not self.user.is_subscribed()

        wrong_token_user = User()
        wrong_token_user.plan_id = "incorrect_token"
        assert not wrong_token_user.is_subscribed()

    def test_cancel_billing(self):
        self.user.subscribe("masonite-flash", "tok_amex")

        assert self.user.is_subscribed("masonite-flash")
        assert self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

        assert not self.user.is_subscribed("masonite-flash")
        assert not self.user.is_subscribed()

    def test_on_trial(self):
        self.user.subscribe("masonite-flash", "tok_amex")
        assert not self.user.on_trial()
        assert self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

        self.user.trial(days=7).subscribe("masonite-flash", "tok_amex")
        assert self.user.on_trial()
        assert self.user.cancel(now=False)
        assert self.user.on_trial()
        assert self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

        assert not self.user.on_trial()

    def test_subscribe_cancel_subscription_at_end_of_period(self):
        self.user.subscribe("masonite-flash", "tok_amex")

        assert self.user.is_subscribed()
        self.user.cancel(now=False)
        assert self.user.is_subscribed()
        self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

        assert not self.user.is_subscribed()

    def test_subscription_is_canceled(self):
        self.user.subscribe("masonite-flash", "tok_amex")

        assert not self.user.is_canceled()
        self.user.cancel(now=False)
        assert self.user.is_canceled()

        self.user.cancel(now=True)
        assert not self.user.is_canceled()

    def test_skip_trial(self):
        self.user.subscribe("masonite-test", "tok_amex")

        assert self.user.on_trial()
        self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

        self.user.skip_trial().subscribe("masonite-test", "tok_amex")

        assert not self.user.on_trial()
        self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

    def test_charge_customer(self):
        self.user.email = "test@email.com"
        assert self.user.charge(999)
        assert self.user.charge(999, token="tok_amex")
        assert self.user.charge(299, metadata={"name": "test"})
        assert self.user.charge(299, description="Charge For test@email.com")

    def test_swap_plan(self):
        self.user.subscribe("masonite-test", "tok_amex")

        assert self.user.is_subscribed("masonite-test")
        assert self.user.swap("masonite-flash")
        assert self.user.is_subscribed()
        assert self.user.is_subscribed("masonite-flash")
        assert not self.user.is_subscribed("masonite-test")

        assert self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

    def test_change_card(self):
        assert self.user.card("tok_amex")

    def test_cancel_and_resume_plan(self):
        self.user.skip_trial().subscribe("masonite-test", "tok_amex")

        # assert user.is_canceled() is False
        assert self.user.cancel()
        assert self.user.is_canceled()
        assert self.user.resume()
        assert not self.user.is_canceled()

        self.user.cancel(now=True)
        if os.environ.get("TEST_ENVIRONMENT") == "travis":
            time.sleep(2)

    def test_plan_returns_plan_name(self):
        self.user.skip_trial().subscribe("masonite-test", "tok_amex")

        assert self.user.plan() == "Masonite Test"

        assert self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

    def test_is_on_trial_after_trial(self):
        self.user.subscribe("masonite-test", "tok_amex")
        assert self.user.on_trial()

        # set the trial to an expired time
        subscription = self.user._get_subscription()
        subscription.trial_ends_at = pendulum.now().subtract(days=1)
        subscription.save()

        assert not self.user.on_trial()
        assert not self.user.on_trial()

        self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

    def test_subscription_is_over(self):
        self.user.skip_trial().subscribe("masonite-test", "tok_amex")
        assert self.user.is_subscribed()
        assert not self.user.on_trial()

        # set the subscription to an expired time
        subscription = self.user._get_subscription()
        subscription.ends_at = pendulum.now().subtract(minutes=1)
        subscription.save()

        assert not self.user.on_trial()

        assert self.user.was_subscribed()
        assert self.user.was_subscribed("masonite-test")
        assert not self.user.was_subscribed("masonite-flash")

        assert not self.user.is_subscribed()

        self.user.cancel(now=True)
        # if os.environ.get('TEST_ENVIRONMENT') == 'travis':
        #     time.sleep(2)

    def test_can_use_coupon_on_charge(self):
        assert self.user.get_driver()._apply_coupon(1000) == 1000
        assert self.user.coupon("5-off").get_driver()._apply_coupon(500) == 400
        assert self.user.coupon("10-percent-off").get_driver()._apply_coupon(1000) == 900
        assert self.user.coupon("10-percent-off").get_driver()._apply_coupon(1499) == 1349.1
        assert self.user.coupon(0.10).get_driver()._apply_coupon(1499) == 1349.1
        assert self.user.coupon(100).get_driver()._apply_coupon(1000) == 900

    def test_can_use_coupon_on_subscription(self):
        self.user.skip_trial().coupon("5-off").subscribe("masonite-test", "tok_amex")
        assert self.user.is_subscribed()
        assert not self.user.on_trial()
        self.user._get_subscription()

        self.user.cancel(now=True)
