from abc import ABC as AbstractBaseClass


class BillingProcessorContract(AbstractBaseClass):

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
        pass

    def coupon(self, coupon_id):
        """Sets the coupon that should be used on inside the subscription arguments.

        Arguments:
            coupon_id {string} -- Stripes coupon ID

        Returns:
            self
        """
        pass

    def trial(self, days):
        """Sets the trial days in the subscription args.

        Keyword Arguments:
            days {int} -- Number of days to put the user on a trial. (default: {0})

        Returns:
            self
        """
        pass

    def cancel(self, plan_id, now=False):
        """Cancel the users subscription

        Arguments:
            plan_id {string} -- The Stripe plan identifier.

        Keyword Arguments:
            now {bool} -- Whether the user should be canceled now or at the end of the billing period. (default: {False})

        Returns:
            False|stripe.subscription.retrieve
        """
        pass

    def charge(self, amount, **kwargs):
        """Charges the user a specific amount of money

        Arguments:
            amount {int} -- The amount to charge the customer in cents.

        Returns:
            bool -- Whether the charge succeeded.
        """
        pass

    def skip_trial(self):
        """Whether the user should skip the trial and be charged right away. 

        This updates the subscription arguments.

        Returns:
            self
        """
        pass

    def swap(self, plan_id, new_plan, **kwargs):
        """Swaps the old plan for a new plan.

        Arguments:
            plan {string} -- The old plan the user currently has.
            new_plan {string} -- The new plan the user should be switched to.

        Returns:
            stripe.Subscription.modify
        """
        pass

    def resume(self, plan_id):
        """Resume the user back on the subscription they may have cancelled.

        Arguments:
            plan_id {string} -- The Stripe plan identifier.

        Returns:
            True
        """
        pass

    def card(self, customer_id, token):
        """Updates the card on file with the user.

        Arguments:
            customer_id {string} -- The Stripe customer identifier. 
            token {string} -- The Stripe token from the form submission.

        Returns:
            True
        """
        pass

    def _create_customer(self, description, token):
        """Creates the customer in Stripe.

        Arguments:
            description {string} -- The customer description.
            token {string} -- The Stripe token from the form submission.

        Returns:
            stripe.Customer.create
        """
        pass
