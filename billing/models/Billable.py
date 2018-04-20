from billing.managers.BillingManager import BillingManager
try:
    from config import billing
    PROCESSOR = BillingManager().create_driver(billing.DRIVER)
except ImportError:
    raise ImportError('No configuration file found')
    

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

        self._save_subscription(subscription, processor_plan)

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
        return PROCESSOR.cancel(self.plan_id, now=now)

    def create_customer(self, description, token):
        return PROCESSOR.create_customer(description, token)
    
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