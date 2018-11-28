""" The Billing Model """

import pendulum

from billing.factories import BillingFactory

from .Subscription import Subscription

try:
    from config import billing
    PROCESSOR = BillingFactory.make(billing.DRIVER)
except ImportError:
    raise ImportError('No configuration file found')


class Billable:

    _processor = PROCESSOR

    def subscribe(self, processor_plan, token):
        """Subscribe user to a billing plan.

        Arguments:
            processor_plan {string} -- The plan inside the processor (Stripe, Braintree etc)
            token {string} -- The authentication token from a form submission

        Returns:
            bool
        """
        if not self.customer_id:
            self.create_customer('Customer {0}'.format(self.email), token)

        if self.is_subscribed(processor_plan):
            return True

        if hasattr(self, 'customer_id'):
            customer_id = self.customer_id
        else:
            customer_id = None

        subscription = self._processor.subscribe(
            processor_plan, token, customer=customer_id)
        self.plan_id = subscription['id']
        self.save()

        # TODO add to subscription model
        self._save_subscription_model(processor_plan, subscription)

        return True

    def coupon(self, coupon_id):
        """A coupon code, an integer or a float as a representation of the coupon.

        Arguments:
            coupon_id {string|integer|float} -- The coupon identification.
                - string - Lookup in the processor for the coupon information
                - integer - deduct directly from the amount
                - float - deduct the percentage amount

        Returns:
            self
        """
        self._processor.coupon(coupon_id)
        return self

    def trial(self, days=False):
        """Put user on trial.

        Keyword Arguments:
            days {bool} -- Specify the days the user should be put on trial. (default: {False})

        Returns:
            self
        """
        self._processor.trial(days)
        return self

    def on_trial(self, plan_id=None):
        """Check if a user is on trial.

        Keyword Arguments:
            plan_id {string} -- The plan identifier (default: {None})

        Returns:
            bool
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
        """Cancel a subscription.

        Keyword Arguments:
            now {bool} -- Whether the user should be cancelled now or when the pay period ends. (default: {False})

        Returns:
            bool -- Whether or not the user has been successfully cancelled.
        """
        cancel = self._processor.cancel(self.plan_id, now=now)

        if cancel:
            if now:
                # delete it now
                subscription = self._get_subscription()
                subscription.ends_at = pendulum.now()
                subscription.trial_ends_at = None
                subscription.save()
                return True
            else:
                # update the ended at date
                subscription = self._get_subscription()
                subscription.ends_at = pendulum.from_timestamp(
                    cancel['current_period_end'])
                subscription.save()
                return True
        return False

    def plan(self):
        """Gets the users plan name.

        Returns:
            string|None -- Returns the plan name or None of the plan does not exist.
        """
        subscription = self._get_subscription()
        if subscription:
            return subscription.plan_name

        return None

    def create_customer(self, description, token):
        """Creates a new customer.

        Arguments:
            description {string} -- Description of the customer like email or ID.
            token {string} -- The token gotten from a form submission. This is processor specific.

        Returns:
            string -- Returns the customer id.
        """
        customer = self._processor._create_customer(description, token)
        self.customer_id = customer['id']
        self.save()
        return self.customer_id

    def quantity(self, quantity):
        """Set a quantity amount for a subscription.

        Arguments:
            quantity {int}

        Returns:
            self
        """
        self._quantity = quantity
        return self

    def charge(self, amount, **kwargs):
        """Charge a one time charge for a user.

        Arguments:
            amount {int} -- The integer in cents.

        Returns:
            processor.charge -- The processor charge method.
        """
        if not kwargs.get('token'):
            kwargs.update({'customer': self.customer_id})
        else:
            kwargs.update({'source': kwargs.get('token')})
            del kwargs['token']

        if not kwargs.get('description'):
            kwargs.update({'description': 'Charge For {0}'.format(self.email)})

        return self._processor.charge(amount, **kwargs)

    def on_grace_period(self):
        """Check if a user is on a grace period
        """
        pass

    def is_subscribed(self, plan_name=None):
        """Check if a user is subscribed.

        Keyword Arguments:
            plan_name {string} -- The plan name or None. If it is None this will check if the user is subscribed.
                                    If a string exists it will check if a user is subscribed to that plan. (default: {None})

        Returns:
            bool -- Whether the user is subscribed or not.
        """
        # If the subscription exists
        if self._get_subscription():
            # If the subscription does not expire OR the subscription ends at a time in the future
            if not self._get_subscription().ends_at or (self._get_subscription().ends_at and self._get_subscription().ends_at.is_future()):
                # If the plan name equals the plan name specified
                if plan_name and self._get_subscription().plan == plan_name:
                    return True

                # if the plan name was left out
                if not plan_name:
                    return True

        return False

    def was_subscribed(self, plan=None):
        """Checks if the user was subscribed at one point but is no longer

        Keyword Arguments:
            plan {string|None} -- The plan name or None. If it is None this will check if the user is subscribed.
                                    If a string exists it will check if a user is subscribed to that plan. (default: {None})

        Returns:
            bool -- Whether the user was subscribed at one point but is not currently subscribed.
        """
        subscription = self._get_subscription()

        if subscription and subscription.ends_at and subscription.ends_at.is_past():
            if plan and subscription.plan == plan:
                return True
            elif not plan:
                return True

        return False

    def is_canceled(self):
        """Check if the user was subscribed but cancelled their subscription. This is useful if the user is on a grace period.

        Returns:
            bool
        """
        subscription = self._get_subscription()

        if not subscription:
            return False

        if not subscription.trial_ends_at and subscription.ends_at and subscription.ends_at.is_future():
            return True

        return False

    def swap(self, new_plan, **kwargs):
        """Change the current plan to a new plan.

        Arguments:
            new_plan {string} -- The new plan to swap to.

        Returns:
            bool   
        """
        trial_ends_at = None
        ends_at = None
        swapped_subscription = self._processor.swap(
            self.plan_id, new_plan, **kwargs)

        if swapped_subscription['trial_end']:
            trial_ends_at = pendulum.from_timestamp(
                swapped_subscription['trial_end'])

        if swapped_subscription['current_period_end']:
            ends_at = pendulum.from_timestamp(
                swapped_subscription['current_period_end'])

        subscription = self._get_subscription()
        subscription.plan = swapped_subscription['plan']['id']
        subscription.plan_name = swapped_subscription['plan']['name']
        subscription.trial_ends_at = trial_ends_at
        subscription.ends_at = ends_at
        return subscription.save()

    def skip_trial(self):
        """Skip any trial that the plan may have and charge the user.

        Returns:
            self
        """
        self._processor.skip_trial()
        return self

    def prorate(self, bool):
        """
        Whether the user should be prorated or not
        TODO: should be only parameters
        """
        pass

    def resume(self):
        """Resume a cancelled subscription

        Returns:
            processor.resume -- Returns the processor resume method.
        """
        plan = self._processor.resume(self.plan_id)
        subscription = self._get_subscription()
        subscription.ends_at = None
        subscription.save()
        return plan

    def card(self, token):
        """Change the card or token used to charge the user.

        Arguments:
            token {string} -- The processor authentication token. Usually submitted from a form.

        Returns:
            processor.card -- Returns the processor card method.
        """
        return self._processor.card(self.customer_id, token)

    def _get_subscription(self):
        """Gets the subscription from the subcriptions table.

        Returns:
            billing.models.Subscription - The billing subscription model.
        """
        return Subscription.where('user_id', self.id).first()

    def _save_subscription_model(self, processor_plan, subscription_object):
        """Saves the plan to the subscription model

        Arguments:
            processor_plan {string} -- The plan name.
            subscription_object {billing.models.Subscription} -- The billing subscription model.

        Returns:
            billing.models.Subscription -- The billing subscription model.
        """
        trial_ends_at = None
        ends_at = None
        if subscription_object['trial_end']:
            trial_ends_at = pendulum.from_timestamp(
                subscription_object['trial_end'])

        if subscription_object['ended_at']:
            ends_at = pendulum.from_timestamp(subscription_object['ended_at'])

        subscription = Subscription.where('user_id', self.id).first()
        if subscription:
            subscription.plan = processor_plan
            subscription.plan_id = subscription_object['id']
            subscription.plan_name = subscription_object['plan']['name']
            subscription.trial_ends_at = trial_ends_at
            subscription.ends_at = ends_at
            subscription.save()
        else:
            # Create a new plan

            subscription = Subscription.create(
                user_id=self.id,
                plan=processor_plan,
                plan_id=subscription_object['id'],
                plan_name=subscription_object['plan']['id'],
                trial_ends_at=trial_ends_at,
                ends_at=ends_at,
            )

        return subscription
