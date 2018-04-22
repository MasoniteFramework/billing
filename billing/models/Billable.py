from billing.managers.BillingManager import BillingManager
from .Subscription import Subscription
import pendulum
try:
    from config import billing
    PROCESSOR = BillingManager().create_driver(billing.DRIVER)
except ImportError:
    raise ImportError('No configuration file found')

class Billable:

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
        subscription = self._get_subscription()

        if not subscription:
            return False
        
        if not plan_id:
            if subscription.trial_ends_at and subscription.trial_ends_at.is_future():
                return True
        
        if subscription.plan == plan_id and subscription.trial_ends_at and subscription.trial_ends_at.is_future():
            return True
        
        return False

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
                subscription.ends_at = pendulum.from_timestamp(cancel['current_period_end'])
                subscription.save()
                return True
        return False
    
    def plan(self):
        subscription = self._get_subscription()
        if subscription:
            return subscription.plan_name
        
        return None

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
        if not plan_name and self._get_subscription() :
            return True
        
        if self._get_subscription() and plan_name and self._get_subscription().plan == plan_name:
            return True
        
        return False

    def is_canceled(self):
        """
        Check if the user was subscribed but cancelled their subscription
        """
        subscription = self._get_subscription()

        if not subscription:
            return False

        if not subscription.trial_ends_at and subscription.ends_at:
            return True
        return False

    """ Upgrading and changing a plan """

    def swap(self, new_plan, **kwargs):
        """
        Change the current plan
        """
        trial_ends_at = None
        ends_at = None
        swapped_subscription  = PROCESSOR.swap(self.plan_id, new_plan, **kwargs)

        if swapped_subscription['trial_end']:
            trial_ends_at = pendulum.from_timestamp(swapped_subscription['trial_end'])
        
        if swapped_subscription['current_period_end']:
            ends_at = pendulum.from_timestamp(swapped_subscription['current_period_end'])

        subscription = self._get_subscription()
        subscription.plan = swapped_subscription['plan']['id']
        subscription.plan_name = swapped_subscription['plan']['name']
        subscription.trial_ends_at = trial_ends_at
        subscription.ends_at = ends_at
        return subscription.save()
        
    
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
        plan = PROCESSOR.resume(self.plan_id)
        subscription = self._get_subscription()
        subscription.ends_at = None
        subscription.save()
        return plan

    
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
            trial_ends_at = pendulum.from_timestamp(subscription_object['trial_end'])
        
        if subscription_object['ended_at']:
            ends_at = pendulum.from_timestamp(subscription_object['ended_at'])

        subscription = Subscription.create(
            user_id = self.id,
            plan = processor_plan,
            plan_id = subscription_object['id'],
            plan_name = subscription_object['plan']['name'],
            trial_ends_at = trial_ends_at,
            ends_at = ends_at,
        )

        return subscription