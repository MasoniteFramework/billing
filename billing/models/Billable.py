from billing.managers.BillingManager import BillingManager
try:
    from config import billing
    PROCESSOR = BillingManager().create_driver(billing.DRIVER)
except ImportError:
    raise ImportError('No configuration file found')
    

class Billable:

    _tax = False
    _trial = 0

    def subscribe(self, local_plan, processor_plan, token):
        """
        Subscribe user to a billing plan
        """
        if hasattr(self, 'customer_id'):
            customer_id = self.customer_id
        else:
            customer_id = None

        return PROCESSOR.subscribe(processor_plan, token, customer=customer_id, trial_period_days=self._trial)
    
    def trial(self, days=False):
        """
        Put user on trial
        """

        self._trial = days
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
        return PROCESSOR.cancel(self.plan_id, now=now)

    def create_customer(self, description, token):
        return PROCESSOR.create_customer(description, token)
    
    def quantity(self, quantity):
        """
        Set a quantity amount for a subscription
        """
        self._quantity = quantity

    def charge(self):
        """
        Charge a one time charge for a user
        """
        pass

    def create(self, token):
        """
        Used to create the transaction
        """

    """ Checking Subscription Status """

    def on_grace_period(self):
        """
        Check if a user is on a grace period
        """
        pass
    
    def is_subscribed(self, plan_name=None):
        """
        Check if a user is subscribed
        """

        return PROCESSOR.is_subscribed(self.plan_id, plan_name=plan_name)

    def is_cancelled(self):
        """
        Check if the user was subscribed but cancelled their subscription
        """
        pass

    """ Upgrading and changing a plan """

    def swap(self):
        """
        Change the current plan
        """
        pass
    
    def skip_trial(self):
        """
        Skip any trial that the plan may have and charge the user
        """
        pass
    
    def prorate(self, bool):
        """
        Whether the user should be prorated or not
        """
        pass
    
    def resume(self):
        """
        Resume a trial
        """
        pass
    
    def upgrade_card(self):
        """
        Change the card or token
        """
        pass

"""
## Creating
* subscribe
    * resubscribing
* trial
    * specify number of days?
* cancel
* quantity
* _tax
* charge
* create

## Checking
* on_trial
* on_grace_period
* is_subscribed
* has_plan
* is_cancelled

## Upgrading
* swap
* skip_trial
* prorate
* resume
* upgrade_card

"""