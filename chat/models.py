from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class ChatMessage(models.Model):
    
    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
            
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    content = models.TextField(
        blank=True, default='',
        verbose_name=_("Message")
    )    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_("Owner"),
        related_name="%(app_label)s_%(class)s_owner_related",
    )
    answer_to = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_answer_to_related",
        verbose_name=_("answer to")
    )
    topic = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_topic_related",
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        verbose_name=_("recipients"),
        related_name="%(app_label)s_%(class)s_recipients_related",
    )
    to = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        verbose_name=_("to"),
        related_name="%(app_label)s_%(class)s_to_related",
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Creation date")
    )
    files = GenericRelation('common.TheFile', related_query_name='chat_message')

    def __str__(self):
        return f'{truncatechars(self.content, 70)}'

    def get_absolute_url(self):
        return reverse(f'admin:chat_{self._meta.model_name}_change', args=[str(self.id)])
