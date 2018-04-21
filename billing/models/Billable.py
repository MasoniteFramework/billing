from billing.managers.BillingManager import BillingManager
from .Subscription import Subscription
import pendulum
try:
    from config import billing
    PROCESSOR = BillingManager().create_driver(billing.DRIVER)
except ImportError:
    raise ImportError('No configuration file found')

'''
does not need to hit Stripe API:
Integrate with a subscriptions table

on_trial
is_subscribed()
plan()
is_canceled()


Needs to be super tested to the max (~100% test coverage)
Needs to do VAT
Needs to do webhooks
    * cancels
    * renewals
    * subscriptions
Can do only Stripe
Only focus on users table
'''

class Billable:

    _tax = False
    _trial = 0

    def subscribe(self, processor_plan, token):
        """
        Subscribe user to a billing plan
        """
        if not self.customer_id:
            self.create_customer('Customer {0}'.format(self.email), token)
        
        if self.is_subscribed(processor_plan):
            return True

        if hasattr(self, 'customer_id'):
            customer_id = self.customer_id
        else:
            customer_id = None

        subscription = PROCESSOR.subscribe(processor_plan, token, customer=customer_id)
        self.plan_id = subscription['id']
        self.save()

        # TODO add to subscription model
        self._save_subscription_model(processor_plan, subscription)

        return True
    
    def trial(self, days=False):
        """
        Put user on trial
        """

        PROCESSOR.trial(days)
        return self

    def on_trial(self, plan_id=None):
        """
        Check if a user is on trial
        """
        if not plan_id:
            plan_id = self.plan_id
        return PROCESSOR.on_trial(plan_id)

    def cancel(self, now=False):
        """
        Cancel a subscription
        """
        cancel = PROCESSOR.cancel(self.plan_id, now=now)

        if cancel:
            if now:
                # delete it now
                self._get_subscription().delete()
                return True
            else:
                # update the ended at date
                subscription = self._get_subscription()
                subscription.ends_at = cancel['ended_at']
                subscription.save()
                return True
        return False


    
    def plan(self):
        return PROCESSOR.plan(self.plan_id)

    def create_customer(self, description, token):
        customer = PROCESSOR._create_customer(description, token)
        self.customer_id = customer['id']
        self.save()
        return self.customer_id
    
    def quantity(self, quantity):
        """
        Set a quantity amount for a subscription
        """
        self._quantity = quantity

    def charge(self, amount, **kwargs):
        """
        Charge a one time charge for a user
        """

        if not kwargs.get('token'):
            kwargs.update({'customer': self.customer_id})
        else:
            kwargs.update({'source': kwargs.get('token')})
            del kwargs['token']
        
        if not kwargs.get('description'):
            kwargs.update({'description': 'Charge For {0}'.format(self.email)})
        
        return PROCESSOR.charge(amount, **kwargs)

    """ Checking Subscription Status """

    def on_grace_period(self):
        """
        Check if a user is on a grace period
        TODO
        """
        pass
    
    def is_subscribed(self, plan_name=None):
        """
        Check if a user is subscribed
        """

        return PROCESSOR.is_subscribed(self.plan_id, plan_name=plan_name)

    def is_canceled(self):
        """
        Check if the user was subscribed but cancelled their subscription
        """
        return PROCESSOR.is_canceled(self.plan_id)

    """ Upgrading and changing a plan """

    def swap(self, new_plan, **kwargs):
        """
        Change the current plan
        """
        return PROCESSOR.swap(self.plan_id, new_plan, **kwargs)
    
    def skip_trial(self):
        """
        Skip any trial that the plan may have and charge the user
        """
        PROCESSOR.skip_trial()
        return self
    
    def prorate(self, bool):
        """
        Whether the user should be prorated or not
        TODO: should be only parameters
        """
        pass
    
    def resume(self):
        """
        Resume a trial
        """
        return PROCESSOR.resume(self.plan_id)
    
    def card(self, token):
        """
        Change the card or token
        """
        return PROCESSOR.card(self.customer_id, token)
    
    def _get_subscription(self):
        return Subscription.where('plan_id', self.plan_id).first()
    
    def _save_subscription_model(self, processor_plan, subscription_object): 

        trial_ends_at = None
        ends_at = None
        if subscription_object['trial_end']:
            trial_ends_at = pendulum.from_timestamp(subscription_object['trial_end']).to_datetime_string()
        
        if subscription_object['ended_at']:
            ends_at = pendulum.from_timestamp(subscription_object['ended_at']).to_datetime_string()

        subscription = Subscription.create(
            user_id = self.id,
            plan = processor_plan,
            plan_id = subscription_object['id'],
            plan_name = subscription_object['plan']['name'],
            quantity = 1,
            trial_ends_at = trial_ends_at,
            ends_at = ends_at,
        )

        return subscription