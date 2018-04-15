import stripe
from stripe.error import InvalidRequestError
from billing.exceptions import PlanNotFound

try:
    from config import billing
    stripe.api_key = billing.DRIVERS['stripe']['secret']
except ImportError:
    raise ImportError('Billing configuration found')

class BillingStripeDriver:

    def subscribe(self, plan, token, customer=None):
        # create a customer
        if not customer:
            customer = self._create_customer('description', token)

        try:
            subscription = self._create_subscription(customer, {'plan': plan})
            return subscription['id']
        except InvalidRequestError as e:
            if 'No such plan' in str(e):
                raise PlanNotFound('The {0} plan was not found in Stripe'.format(plan))
            if 'No such customer' in str(e):
                return False
        
        return None
        
    def is_subscribed(self, customer_id, plan_name=None):
        try:
            # get the customer
            customer = stripe.Customer.retrieve(customer_id)
            if plan_name is None and 'plan' in customer['subscriptions']['data'][0]['items']['data'][0]:
                return True
            if plan_name in customer['subscriptions']['data'][0]['items']['data'][0]['plan']['id']:
                return True
            return False
        except InvalidRequestError:
            return False
        except IndexError:
            return False
        return None
    
    def cancel(self, plan_id):
        subscription = stripe.Subscription.retrieve(plan_id)
        delete = subscription.delete()
        if delete['status'] == 'canceled':
            return True
        return False

    def create_customer(self, description, token):
        customer = self._create_customer('test-customer', 'tok_amex')
        return customer['id']

    def _create_customer(self, description, token):
        return stripe.Customer.create(
            description=description,
            source=token # obtained with Stripe.js
        )
    
    def _create_subscription(self, customer, items):
        if not isinstance(customer, str):
            customer = customer['id']

        return stripe.Subscription.create(
            customer=customer,
            items=[items]
        )