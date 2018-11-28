''' Masonite Billing Controller For Webhooks '''

from billing.models import Subscription
from config import auth
import pendulum


class WebhookController:
    """
    Add webhooks to tie into stripe events
    """

    model = auth.AUTH['model']

    def handle(self, Request):
        """
        Entry Point for all webhooks
        """

        # Turn the hook into a method call
        payload = Request.input('payload')
        handler = payload['type'].split('.')
        handler = 'handle_' + '_'.join(handler)

        if hasattr(self, handler):
            return getattr(self, handler)(payload)

        return 'Webhook Not Supported'
    
    def handle_customer_subscription_deleted(self, payload):
        """
        Event for subscription has ended
        """
        subscription_info = payload['data']['object']
        user = self.model.where('customer_id', subscription_info['customer']).first()

        if user:
            subscription = Subscription.where(
                'plan_id', subscription_info['items']['data'][0]['subscription']
            ).first()
            if subscription:
                subscription.ends_at = pendulum.now()
                subscription.save()
                return 'Webhook Handled'

        return 'Webhook Error'

