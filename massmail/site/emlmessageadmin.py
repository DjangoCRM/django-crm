import threading
from django.contrib import admin
from django.template import Context
from django.template import Template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.admin import FileInline
from common.utils.copy_files import copy_files
from common.utils.get_signature_preview import get_rendered_context
from common.utils.get_signature_preview import get_signature_preview
from common.utils.helpers import CONTENT_COPY_ICON
from common.utils.helpers import CONTENT_COPY_LINK
from common.utils.helpers import COPY_STR
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from massmail.models import EmlMessage
from massmail.models import Signature

_thread_local = threading.local()


class EmlMessageAdmin(CrmModelAdmin):

    inlines = [FileInline]
    list_display = (
        'subject',
        'person',
        'update_date',
        'content_copy',
        'id'
    )
    list_filter = (ByOwnerFilter,)
    list_per_page = 30
    readonly_fields = (
        'department',
        'modified_by',
        'signature_preview',
        'msg_preview',
        'content_copy'
    )
    search_fields = ("subject", "content")
    
    # -- ModelAdmin methods -- #

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        emlmessage_id = request.GET.get('copy_emlmessage')
        if emlmessage_id:
            emlmessage = EmlMessage.objects.get(id=emlmessage_id)
            initial['subject'] = emlmessage.subject
            initial['content'] = emlmessage.content
            initial['is_html'] = emlmessage.is_html

        if 'signature' not in initial:
            signature = Signature.objects.filter(
                owner=request.user, default=True
            ).first()
            initial['signature'] = signature
            _thread_local.signature = signature
        return initial

    def get_fieldsets(self, request, obj=None):
        fieldsets = []
        if obj:
            fieldsets.append(
                (_('Preview'), {
                    'fields': ('msg_preview', 'signature_preview')
                })
            )
        fieldsets.extend([
            (_('Edit'), {
                'fields': (
                    'subject',
                    'content',
                    'signature'
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    ('owner', 'department'),
                    # ('creation_date', 'update_date')
                )
            }),
        ])

        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "signature":
                kwargs["queryset"] = Signature.objects.filter(
                    owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'signature' in form.base_fields:
            field = form.base_fields["signature"]
            field.widget.can_view_related = False        
        return form

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        emlmessage_id = request.GET.get('copy_emlmessage')
        if emlmessage_id:
            emlmessage = EmlMessage.objects.get(id=emlmessage_id)
            files = emlmessage.files.all()
            if files:
                copy_files(emlmessage, form.instance)

    # -- ModelAdmin callables -- #

    @admin.display(description='')
    def content_copy(self, obj):
        url = reverse("site:massmail_emlmessage_add") + f"?copy_emlmessage={obj.id}"
        return mark_safe(CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON))

    @admin.display(description=_("Message"))
    def msg_preview(self, obj):
        load_mailbuilder = "{% load mailbuilder %}"
        content = f"""
        {load_mailbuilder} 
        SUBJECT: {obj.subject}<br>
        {obj.content}<br>
        """
        template = Template(content)
        context = Context({'preview': True})
        return get_rendered_context(template, context)

    @admin.display(description=_("Signature"))
    def signature_preview(self, obj):
        if obj:
            if obj.signature:
                return get_signature_preview(obj.signature)
            else:
                return get_signature_preview(_thread_local.signature)
        return ''
