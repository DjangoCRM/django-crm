from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from crm.site.crmadminsite import crm_site
from django.urls import path, include
from django.views.generic.detail import DetailView

from common.views.export_objects import export_objects_view
from crm.views.create_email import create_email
from crm.views.add_request import add_request
from crm.views.delete_duplicate_object import DeleteDuplicateObject
from crm.views.download_original_email import download_original_email
from crm.views.reply_email import reply_email
from crm.views.got_massmails import got_company_massmails
from crm.views.got_massmails import got_contacts_massmails
from crm.views.got_massmails import got_leads_massmails
from crm.views.view_original_email import view_original_email
from crm.views.change_owner_companies import change_owner_companies


urlpatterns = [
    path('', crm_site.urls),

    path(
        'delete-duplicate/<int:content_type_id>/<int:object_id>/',
        login_required(DeleteDuplicateObject.as_view()),
        name='delete_duplicate'
    ),

    path('change-owner-companies/', login_required(change_owner_companies), name='change_owner_companies'),

    path(
        'export-objects/', staff_member_required(export_objects_view),
        name="export_objects"
    ),

    path(
        'create-email/<int:object_id>',
        staff_member_required(create_email),
        name='create_email'
    ),
    path('reply_email/<int:object_id>/', staff_member_required(reply_email), name='reply_email'),

    path(
        'print-email/<int:object_id>',
        staff_member_required(DetailView.as_view(
            model=apps.get_model('crm', 'CrmEmail'),
            pk_url_kwarg='object_id',
            template_name='crm/print_email.html'
        )),
        name='print_email'
    ),
    path(
        'print-request/<int:object_id>',
        staff_member_required(DetailView.as_view(
            model=apps.get_model('crm', 'Request'),
            pk_url_kwarg='object_id',
            template_name='crm/print_request.html'
        )),
        name='print_request'
    ),
    path('add-request/', add_request, name='add_request'),
    path(
        'got-contacts-massmails/<int:object_id>/',
        staff_member_required(got_contacts_massmails),
        name='got_contacts_massmails'
    ),
    path(
        'got-company-massmails/<int:object_id>/',
        staff_member_required(got_company_massmails),
        name='got_company_massmails'
    ),
    path(
        'got-leads-massmails/<int:object_id>/',
        staff_member_required(got_leads_massmails),
        name='got_leads_massmails'
    ),
    path(
        'view-original-email/<int:object_id>/',
        staff_member_required(view_original_email),
        name='view_original_email'
    ),
    path(
        'view-original-email-uid/<int:ea_id>/<int:uid>/',
        staff_member_required(view_original_email),
        name='view_original_email_uid'
    ),
    path('', include('massmail.urls')),
    path(
        'download-original-email/<int:object_id>/',
        staff_member_required(download_original_email),
        name='download_original_email'
    ),
]
