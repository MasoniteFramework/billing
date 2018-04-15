import stripe
from stripe.error import InvalidRequestError
from billing.exceptions import PlanNotFound

try:
    from config import billing
    stripe.api_key = billing.DRIVERS['stripe']['secret']
except ImportError:
    raise ImportError('Billing configuration found')

class BillingStripeDriver:

    def subscribe(self, plan, token):
        # create a customer
        customer = self._create_customer('description', token)

        try:
            subscription = self._create_subscription(customer, {'plan': plan})
        except InvalidRequestError:
            raise PlanNotFound('The {0} plan was not found in Stripe'.format(plan))
        
        return subscription['id']
    
    def is_subscribed(self):
        pass
    
    def _create_customer(self, description, token):
        return stripe.Customer.create(
            description=description,
            source=token # obtained with Stripe.js
        )
    
    def _create_subscription(self, customer, items):
        return stripe.Subscription.create(
            customer=customer['id'],
            items=[items]
        )