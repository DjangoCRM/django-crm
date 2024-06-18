from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from common.models import UserProfile
from common.utils.helpers import USER_MODEL


@receiver(post_save, sender=USER_MODEL)
def user_creation_handler(sender, instance, created, **kwargs):
    if created:
        co_workers = Group.objects.get(name='co-workers')
        instance.groups.add(co_workers)
        UserProfile.objects.create(user=instance)
