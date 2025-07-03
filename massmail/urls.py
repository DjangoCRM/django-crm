from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from massmail.views.copy_message import copy_message
from massmail.views.exclude import exclude_recipients
from massmail.views.file_upload import file_upload
from massmail.views.get_oauth2_tokens import request_authorization_code
from massmail.views.message_previews import message_preview
from massmail.views.recipient_ids import view_recipient_ids
from massmail.views.select_recipient_type import select_recipient_type
from massmail.views.send_failed_recipients import send_failed_recipients
from massmail.views.send_tests import send_test
from massmail.views.show_uploaded_images import show_uploaded_images
from massmail.views.signature_previews import signature_preview
from massmail.views.unsubscribes import unsubscribe


urlpatterns = [
    path(
        'message-preview/<int:message_id>/',
        login_required(message_preview),
        name='message_preview'
    ),
    path(
        'signature-preview/',
        login_required(signature_preview),
        name='signature_preview'
    ),
    path(
        'send-test/<int:message_id>/',
        staff_member_required(send_test),
        name='send_test'
    ),
    path(
        'send-failed-recipients/<int:object_id>/', 
        staff_member_required(send_failed_recipients), 
        name='send_failed_recipients'
    ),
    path(
        'successful-ids/<int:object_id>/', 
        staff_member_required(view_recipient_ids),
        {'method': 'get_successful_ids'},
        name='successful_ids'
    ),
    path(
        'failed-ids/<int:object_id>/', 
        staff_member_required(view_recipient_ids),
        {'method': 'get_failed_ids'},
        name='failed_ids'
    ),
    path(
        'copy-message/<int:object_id>/', 
        staff_member_required(copy_message), 
        name='copy_message'
    ),
    path(
        'unsubscribe/<uuid:recipient_uuid>/',
        unsubscribe,
        name='unsubscribe'
    ),
    path(
        'request-authorization-code/<int:email_account_id>/', 
        staff_member_required(request_authorization_code), 
        name='request_authorization_code'
    ),
    path(
        'pic-upload/',
        staff_member_required(file_upload),
        name='pic_upload'
    ),
    path(
        'show-uploaded-images/',
        staff_member_required(show_uploaded_images),
        name='show_uploaded_images'
    ),
    path(
        'select-recipient-type/',
        staff_member_required(select_recipient_type),
        name='select_recipient_type'
    ),
    path(
        'exclude-recipients/<int:object_id>/',
        staff_member_required(exclude_recipients),
        name='exclude_recipients'
    ),
]
