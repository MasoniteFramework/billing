from orator.migrations import Migration


class MakeSubscriptionsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('subscriptions') as table:
            table.increments('id')
            table.integer('user_id').unsigned()
            table.string('plan')
            table.string('plan_id')
            table.string('plan_name')
            table.timestamp('trial_ends_at').nullable()
            table.timestamp('ends_at').nullable()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('subscriptions')
