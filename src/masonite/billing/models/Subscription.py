from masoniteorm.models import Model


class Subscription(Model):
    __fillable__ = [
        "user_id",
        "plan",
        "plan_id",
        "plan_name",
        "trial_ends_at",
        "ends_at",
    ]

    __dates__ = ["trial_ends_at", "ends_at"]
