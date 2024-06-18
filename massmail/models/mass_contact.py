import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class MassContact(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    email_account = models.ForeignKey(
        'EmailAccount', null=True, blank=True, 
        on_delete=models.CASCADE
        )
    massmail = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
         
    def set_masscontact(self, email_account):
        self.email_account = email_account
        self.save()  
      
    def __str__(self):
        return str(self.content_object)
