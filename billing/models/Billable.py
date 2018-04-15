from billing.managers.BillingManager import BillingManager
try:
    from config import billing
    PROCESSOR = BillingManager().create_driver(billing.DRIVER)
except ImportError:
    raise ImportError('No configuration file found')
    

class Billable:

    _tax = False

    def subscribe(self, local_plan, processor_plan, token):
        """
        Subscribe user to a billing plan
        """
        return PROCESSOR.subscribe(processor_plan, token)
    
    def trial(self):
        """
        Put user on trial
        """
        return PROCESSOR.trial()
    
    def cancel(self):
        """
        Cancel a subscription
        """
        return PROCESSOR.cancel()
    
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

    def on_trial(self):
        """
        Check if a user is on trial
        """
        pass
    
    def on_grace_period(self):
        """
        Check if a user is on a grace period
        """
        pass
    
    def is_subscribed(self):
        """
        Check if a user is subscribed
        """
        return PROCESSOR.is_subscribed()
    
    def has_plan(self):
        """
        Check if a user is on a specific plan
        """
        pass

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