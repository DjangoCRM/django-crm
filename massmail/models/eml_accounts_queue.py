import json
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EmlAccountsQueue(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="queue_owners"
    )
    queue = models.TextField(
        max_length=100, null=False, blank=False,
        default='[]',
        help_text=_("The queue of the user email accounts.")
    )

    def get_queue(self):
        queue = json.loads(self.queue)
        if not self.queue:
            queue = list()
        return queue

    @property
    def length(self):
        queue = self.get_queue()
        return len(queue)

    def get_next(self):
        queue = self.get_queue()
        if queue:
            account_id = queue.pop(0)
            queue.append(account_id)
            self.queue = json.dumps(queue)
            self.save()
        else:
            account_id = None
        return account_id

    def add_id(self, account_id):
        queue = self.get_queue()
        if account_id not in queue:
            queue.append(account_id)
            self.queue = json.dumps(queue)
            self.save()

    def remove_id(self, account_id):
        queue = self.get_queue()
        if account_id in queue:
            queue.remove(account_id)
            self.queue = json.dumps(queue)
            self.save()

    def __str__(self):
        if self.owner:
            return f'{self.owner.username} queue'   # NOQA
        else:
            return f'Queue ID{self.id}'
