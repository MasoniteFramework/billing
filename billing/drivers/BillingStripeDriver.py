""" The Stripe Billing Driver """

import pendulum
import stripe
from stripe.error import InvalidRequestError

from billing.exceptions import PlanNotFound

try:
    from config import billing
    stripe.api_key = billing.DRIVERS['stripe']['secret']
except ImportError:
    raise ImportError('Billing configuration found')


class BillingStripeDriver:

    _subscription_args = {}

    def subscribe(self, plan, token, customer=None, **kwargs):
        """Subscribe user to a billing plan.

        Arguments:
            plan {string} -- The plan inside stripe.
            token {string} -- The authentication token from a form submission.


        Keyword Arguments:
            customer {None|string} -- If None then the customer will be created based on the user. 
                                        Else it requires the customer ID. (default: {None})

        Raises:
            PlanNotFound -- Raised when the plan is not found.

        Returns:
            billing.models.Subscription - The subscription billing model.
        """
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
                raise PlanNotFound(
                    'The {0} plan was not found in Stripe'.format(plan))
            if 'No such customer' in str(e):
                return False

        return None

    def coupon(self, coupon_id):
        """Sets the coupon that should be used on inside the subscription arguments.

        Arguments:
            coupon_id {string} -- Stripes coupon ID

        Returns:
            self
        """
        self._subscription_args.update({'coupon': coupon_id})

        return self

    def trial(self, days=0):
        """Sets the trial days in the subscription args.

        Keyword Arguments:
            days {int} -- Number of days to put the user on a trial. (default: {0})

        Returns:
            self
        """
        self._subscription_args.update({'trial_period_days': days})
        return self

    def on_trial(self, plan_id=None):
        """Checks if the user in on a trial

        Keyword Arguments:
            plan_id {string|None} -- If the argument is None it will look up the users current plan. Else
                                        it will find out if the user is subscribed to the plan given. (default: {None})

        Returns:
            bool
        """
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
        """Checks if the user is subscribed.

        Arguments:
            plan_id {string} -- The plan identifier to check for

        Keyword Arguments:
            plan_name {string|None} -- The plan name the user should be subscribed to. (default: {None})

        Returns:
            bool
        """
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
        """If the user is cancelled.

        Arguments:
            plan_id {string} -- The Stripe plan identifier

        Returns:
            bool
        """
        try:
            # get the plan
            subscription = self._get_subscription(plan_id)
            if subscription['cancel_at_period_end'] is True and subscription['status'] == 'active':
                return True
        except InvalidRequestError:
            return False

        return False

    def cancel(self, plan_id, now=False):
        """Cancel the users subscription

        Arguments:
            plan_id {string} -- The Stripe plan identifier.

        Keyword Arguments:
            now {bool} -- Whether the user should be canceled now or at the end of the billing period. (default: {False})

        Returns:
            False|stripe.subscription.retrieve
        """
        subscription = stripe.Subscription.retrieve(plan_id)

        if subscription.delete(at_period_end=not now):
            return subscription
        return False

    def create_customer(self, description, token):
        """Created the customer in Stripe.

        Arguments:
            description {string} -- The description of the customer
            token {string} -- The Stripe token from the form submission

        Returns:
            stripe.Customer.create
        """
        return self._create_customer(description, token)

    def skip_trial(self):
        """Whether the user should skip the trial and be charged right away. 

        This updates the subscription arguments.

        Returns:
            self
        """
        self._subscription_args.update({'trial_end': 'now'})
        return self

    def charge(self, amount, **kwargs):
        """Charges the user a specific amount of money

        Arguments:
            amount {int} -- The amount to charge the customer in cents.

        Returns:
            bool -- Whether the charge succeeded.
        """
        if not kwargs.get('currency'):
            kwargs.update({'currency': billing.DRIVERS['stripe']['currency']})

        amount = self._apply_coupon(amount)

        charge = stripe.Charge.create(
            amount=amount,
            **kwargs
        )

        if charge['status'] == 'succeeded':
            return True
        else:
            return False

    def card(self, customer_id, token):
        """Updates the card on file with the user.

        Arguments:
            customer_id {string} -- The Stripe customer identifier. 
            token {string} -- The Stripe token from the form submission.

        Returns:
            True
        """
        stripe.Customer.modify(customer_id,
                               source=token,
                               )

        return True

    def swap(self, plan, new_plan, **kwargs):
        """Swaps the old plan for a new plan.

        Arguments:
            plan {string} -- The old plan the user currently has.
            new_plan {string} -- The new plan the user should be switched to.

        Returns:
            stripe.Subscription.modify
        """
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
        """Resume the user back on the subscription they may have cancelled.

        Arguments:
            plan_id {string} -- The Stripe plan identifier.

        Returns:
            True
        """
        subscription = stripe.Subscription.retrieve(plan_id)
        stripe.Subscription.modify(plan_id,
                                   cancel_at_period_end=False,
                                   items=[{
                                       'id': subscription['items']['data'][0].id
                                   }]
                                   )
        return True

    def plan(self, plan_id):
        """Gets the subscription by the plan identifier.

        Arguments:
            plan_id {string} -- The stripe plan identifier.

        Returns:
            string -- Returns the plan name.
        """
        subscription = self._get_subscription(plan_id)
        return subscription['plan']['name']

    def _apply_coupon(self, amount):
        """Applies the coupon code to the subscription.

        Arguments:
            amount {string|int|float} -- If the coupon amount or identifier.
                - string - Lookup in the processor for the coupon information
                - integer - deduct directly from the amount
                - float - deduct the percentage amount

        Returns:
            int - Returns the amount that was just charged.
        """
        if 'coupon' in self._subscription_args:
            if type(self._subscription_args['coupon']) == str:
                coupon = stripe.Coupon.retrieve(
                    self._subscription_args['coupon'])
                if coupon['percent_off']:
                    return abs((amount * (coupon['percent_off'] / 100)) - amount)

                return amount - coupon['amount_off']
            elif type(self._subscription_args['coupon']) == int:
                return amount - self._subscription_args['coupon']
            elif type(self._subscription_args['coupon']) == float:
                return abs((amount * (self._subscription_args['coupon'])) - amount)

        return amount

    def _create_customer(self, description, token):
        """Creates the customer in Stripe.

        Arguments:
            description {string} -- The customer description.
            token {string} -- The Stripe token from the form submission.

        Returns:
            stripe.Customer.create
        """
        return stripe.Customer.create(
            description=description,
            source=token  # obtained with Stripe.js
        )

    def _create_subscription(self, customer, **kwargs):
        """Creates the subscription.

        Arguments:
            customer {string|object} -- The customer object or identifier.

        Returns:
            stripe.Subscription.create
        """
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
        """Gets the subscription based on the plan identifier.

        Arguments:
            plan_id {string} -- The Stripe plan identifier.

        Returns:
            stripe.Subscription.retrieve
        """
        return stripe.Subscription.retrieve(plan_id)
