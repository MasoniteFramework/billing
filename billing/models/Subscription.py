from config.database import Model

class Subscription(Model):
    __fillable__ = ['user_id', 'plan', 'plan_id', 'plan_name', 'quantity', 'trial_ends_at', 'ends_at']