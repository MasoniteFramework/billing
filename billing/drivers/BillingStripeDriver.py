import stripe
from stripe.error import InvalidRequestError
from billing.exceptions import PlanNotFound
import pendulum

try:
    from config import billing
    stripe.api_key = billing.DRIVERS['stripe']['secret']
except ImportError:
    raise ImportError('Billing configuration found')

class BillingStripeDriver:

    _subscription_args = {}

    def subscribe(self, plan, token, customer=None, **kwargs):
        # create a customer
        if not customer:
            customer = self._create_customer('description', token)

        try:
            subscription = self._create_subscription(customer,
                plan=plan,
                **kwargs
            )
            return subscription

        except InvalidRequestError as e:
            if 'No such plan' in str(e):
                raise PlanNotFound('The {0} plan was not found in Stripe'.format(plan))
            if 'No such customer' in str(e):
                return False
        
        return None

    def trial(self, days=0):
        self._subscription_args.update({'trial_period_days': days})
        return self

    def on_trial(self, plan_id=None):
        try:
            if plan_id:
                subscription = self._get_subscription(plan_id)
                
                if subscription['status'] == 'trialing':
                    return True
                return False
            
        except InvalidRequestError:
            return False
        return None
        
    def is_subscribed(self, plan_id, plan_name=None):
        try:
            # get the plan
            subscription = self._get_subscription(plan_id)
            if not plan_name:
                if subscription['status'] in ('active', 'trialing'):
                    return True
            
            if subscription["items"]["data"][0]['plan']['id'] == plan_name:
                return True

        except InvalidRequestError:
            return False
        
        return False
    
    def is_canceled(self, plan_id):
        try:
            # get the plan
            subscription = self._get_subscription(plan_id)
            if subscription['cancel_at_period_end'] is True and subscription['status'] == 'active':
                return True
        except InvalidRequestError:
            return False
        
        return False
    
    def cancel(self, plan_id, now=False):
        subscription = stripe.Subscription.retrieve(plan_id)

        if subscription.delete(at_period_end= not now):
            return subscription
        return False

    def create_customer(self, description, token):
        return self._create_customer('test-customer', 'tok_amex')

    def skip_trial(self):
        self._subscription_args.update({'trial_end': 'now'})
        return self
    
    def charge(self, amount, **kwargs):
        if not kwargs.get('currency'):
            kwargs.update({'currency': billing.DRIVERS['stripe']['currency']})

        charge = stripe.Charge.create(
            amount=amount,
            **kwargs
        )

        if charge['status'] == 'succeeded':
            return True
        else:
            return False
        
    def card(self, customer_id, token):
        stripe.Customer.modify(customer_id,
            source=token,
        )

        return True

    def swap(self, plan, new_plan, **kwargs):
        subscription = stripe.Subscription.retrieve(plan)
        subscription = stripe.Subscription.modify(plan,
        cancel_at_period_end=False,
        items=[{
            'id': subscription['items']['data'][0].id,
            'plan': new_plan,
        }]
        )
        return subscription

    def resume(self, plan_id):
        subscription = stripe.Subscription.retrieve(plan_id)
        stripe.Subscription.modify(plan_id,
        cancel_at_period_end = False,
        items=[{
            'id': subscription['items']['data'][0].id
        }]
        )
        return True
    
    def plan(self, plan_id):
        subscription = self._get_subscription(plan_id)
        return subscription['plan']['name']


    def _create_customer(self, description, token):
        return stripe.Customer.create(
            description=description,
            source=token # obtained with Stripe.js
        )
    
    def _create_subscription(self, customer, **kwargs):
        if not isinstance(customer, str):
            customer = customer['id']

        for key, value in self._subscription_args.items():
            kwargs[key] = value

        subscription = stripe.Subscription.create(
            customer=customer,
            **kwargs
        )
        self._subscription_args = {}
        return subscription
    
    def _get_subscription(self, plan_id):  
        return stripe.Subscription.retrieve(plan_id)