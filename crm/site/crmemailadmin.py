import threading
from django.contrib import admin
from django.contrib import messages
from django.db.models import IntegerField
from django.db.models import OuterRef, Subquery
from django.http import HttpResponseRedirect
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from common.admin import FileInline
from common.models import TheFile
from common.admin import InlineFileForm
from common.utils.get_signature_preview import get_signature_preview
from crm.forms.admin_forms import IoMail
from crm.models import CrmEmail
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from crm.utils.admfilters import MailboxFilter
from crm.utils.create_email_request import create_email_request
from crm.utils.clarify_permission import clarify_permission
from crm.settings import KEEP_TICKET
from crm.utils.send_email import send_email
from crm.utils.ticketproc import get_ticket_str
from massmail.models import EmailAccount
from massmail.models import Signature

_thread_local = threading.local()
signature_str = _("Signature")
unsent_emails_str = _("Please note that this is a list of unsent emails.")
inbox_icon = '<i class="material-icons" style="color: var(--green-fg)">archive</i>'
sentbox_icon = '<i class="material-icons" style="color: var(--primary)">unarchive</i>'
outbox_icon = '<i class="material-icons" style="color: var(--error-fg)">unarchive</i>'
trashbox_icon = '<i class="material-icons" style="color: var(--close-button-bg)">delete_forever</i>'


class TheMailFileForm(InlineFileForm):
    class Meta(InlineFileForm.Meta):
        fields = ('attached_to_deal', 'file')


class MailFileInline(FileInline):
    fields = None
    form = TheMailFileForm

    def get_fieldsets(self, request, obj=None):
        fieldsets = ((
            None,
            {'fields': ['file']}
        ),)
        if obj and obj.deal and self.has_change_permission(request, obj):
            fieldsets = ((
                None,
                {'fields': ['file', 'attached_to_deal']}
            ),)
        return fieldsets


class CrmEmailAdmin(CrmModelAdmin):
    change_form_template = 'admin/crm/crmemail/change_form.html'
    form = IoMail
    inlines = [MailFileInline]
    list_display = (
        'the_subject',
        'from_field',
        'to',
        'box',
        'attachment',
        'person',
        'the_creation_date',
        'uid'
    )
    list_filter = (MailboxFilter, ByOwnerFilter)
    list_per_page = 30
    ordering = ['-creation_date']
    raw_id_fields = (
        'lead',
        'contact',
        'company',
        'deal',
        'request'
    )
    search_fields = [
        'to',
        'cc',
        'from_field',
        'subject',
        'content',
        'uid'
    ]
    view_on_site = True

    # -- ModelAdmin methods -- #

    def change_view(self,  request, object_id,
                    form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            url = self.get_url_if_no_object(request, object_id)
            if url:
                return HttpResponseRedirect(url)
            obj = CrmEmail.objects.get(id=object_id)
            if obj.ticket:
                emails = CrmEmail.objects.filter(ticket=obj.ticket).values('id')
                next_emails = emails.filter(creation_date__gt=OuterRef('creation_date'))
                prev_emails = emails.order_by('-creation_date').filter(
                    creation_date__lt=OuterRef('creation_date')
                )
                an_email = emails.filter(id=obj.id).annotate(
                    next_email=Subquery(next_emails[:1], output_field=IntegerField()),
                    prev_email=Subquery(prev_emails[:1], output_field=IntegerField())
                ).first()
                if an_email['next_email']:
                    extra_context['next_email_url'] = reverse(
                        'site:crm_crmemail_change',
                        args=(an_email['next_email'],)
                    )
                if an_email['prev_email']:
                    extra_context['prev_email_url'] = reverse(
                        'site:crm_crmemail_change',
                        args=(an_email['prev_email'],)
                    )
            if obj.deal:
                extra_context['deal_url'] = obj.deal.get_absolute_url()
            elif obj.request:
                extra_context['request_url'] = obj.request.get_absolute_url()
        if request.user.is_superuser:
            extra_context['admin_url'] = reverse('admin:crm_crmemail_change', args=(object_id,))
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = _("Emails in the CRM database.")       
        mailbox = request.GET.get("mailbox")
        if mailbox == "outbox":
            messages.warning(
                request,
                unsent_emails_str
            )            
        return super().changelist_view(
            request, extra_context=extra_context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "signature":
                kwargs["queryset"] = Signature.objects.filter(
                    owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'ticket' in initial:
            initial['subject'] += get_ticket_str(initial['ticket'])
            initial['content'] = KEEP_TICKET % initial['ticket']
        if 'from_field' not in initial:
            ea = EmailAccount.objects.filter(
                owner=request.user, main=True
            ).first()
            initial['from_field'] = ea.from_email if ea else ''
        if 'department' not in initial:
            initial['department'] = request.user.department_id
        if 'signature' not in initial:
            signature = Signature.objects.filter(
                owner=request.user, default=True
            ).first()
            initial['signature'] = signature
            _thread_local.signature = signature
        return initial

    def get_fieldsets(self, request, obj=None):
        fields = [
            ('from_field', 'creation_date'),
            'to', 'cc', 'bcc', 'subject'
        ]
        other_fields = [
            'content',
            'signature_preview',
            'signature',
            'prev_corr'
        ]
        if obj:
            if obj.uid or obj.incoming:
                if not obj.cc:
                    fields.remove('cc')
                if not obj.bcc:
                    fields.remove('bcc')
                fields.append('readonly_content')
            else:
                fields.append('read_receipt')
                
                if obj.owner and request.user != obj.owner:
                    fields.append('readonly_content')
                    fields.append('signature_preview')

                    if not obj.uid and obj.sent:
                        if obj.prev_corr:
                            fields.append('readonly_prev_corr')
                    else:
                        fields.append('prev_corr')
                else:
                    fields.extend(other_fields)
        else:
            fields.append('read_receipt')
            fields.extend(other_fields)
            fields.remove('prev_corr')

        return [
            (None, {'fields': fields}),
            (_('Relations'), {
                'classes': ('collapse',),
                'fields': (
                    'company',
                    'contact',
                    'lead',
                    'deal',
                    'request'
                )
            })
        ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'signature' in form.base_fields:
            field = form.base_fields['signature']
            field.widget.can_view_related = False
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'modified_by', 'uid', 'creation_date',
            'readonly_content', 'readonly_prev_corr',
            'attachment', 'person', 'the_creation_date',
            'the_subject', 'signature_preview',
        ]
        if obj:
            readonly_fields.extend(('owner', 'ticket',))
        if not request.user.is_superuser:
            readonly_fields.extend(('sent', 'incoming', 'inquiry', 'trash'))
        return readonly_fields

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if not obj:
            return value
        if not value:
            # if user is deal co_owner?
            if getattr(obj, 'deal', None) and request.user.is_manager:
                if request.user in (obj.deal.owner, obj.deal.co_owner):
                    return True
            return value
        if obj.incoming or obj.uid:
            return False
        return clarify_permission(request, obj)

    def response_post_save_add(self, request, obj):
        if '_send' in request.POST:
            return send_email(request, obj)
        return super().response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        url = ''
        if '_reply' in request.POST:
            url = reverse('reply_email', args=(obj.pk,)) + '?act=reply'
        elif '_reply-all' in request.POST:
            url = reverse('reply_email', args=(obj.pk,)) + '?act=reply-all'
        elif '_forward' in request.POST:
            url = reverse('reply_email', args=(obj.pk,)) + '?act=forward'
        elif '_send' in request.POST:
            return send_email(request, obj)
        if url:
            return HttpResponseRedirect(url)
        return super().response_post_save_change(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.signature:
            obj.signature = Signature.objects.filter(
                owner=request.user,
                default=True
            ).first()
        if not change:
            ticket = request.GET.get('ticket')
            deal_id = request.GET.get('deal_id')
            request_id = request.GET.get('request_id')
            contact_id = request.GET.get('contact_id')
            lead_id = request.GET.get('lead_id')
            company_id = request.GET.get('company_id')

            if not obj.ticket and ticket:
                obj.ticket = ticket

            if not obj.deal and deal_id:
                obj.deal_id = deal_id                
            
            if not obj.request and request_id:
                obj.request_id = request_id
                            
            if not obj.contact and contact_id:
                obj.contact_id = contact_id

            elif not obj.lead and lead_id:
                obj.lead_id = lead_id
            
            elif not obj.company and company_id:
                obj.company_id = company_id
                
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if not change and obj.inquiry:
            create_email_request(obj)
        file_formset = next((
            f for f in formsets
            if f.model == TheFile
        ), None)
        if file_formset:
            for file_form in file_formset:
                if 'attached_to_deal' in file_form.changed_data:
                    file = file_form.instance
                    if file_form.cleaned_data['attached_to_deal']:
                        file.id = None
                        file.content_object = obj.deal
                        file.save()
                    else:
                        files = obj.deal.files.all()
                        file = next((
                            f for f in files
                            if f.file.name.split('/')[-1].split('.')[0] in file.file.name
                        ), None)
                        if file:
                            file.delete()

    # -- ModelAdmin callables -- #

    @admin.display(description=_('Box'))
    def box(self, obj):
        parameter_name = MailboxFilter.parameter_name
        if obj.sent and not obj.trash:
            value = getattr(_thread_local, "mailbox=sent", None)
            if not value:
                url = self.get_url_for_callable(
                    parameter_name, 'sent')
                value = mark_safe(f'<a title="{_("sent")}" href="{url}">{sentbox_icon}</a>')
                setattr(_thread_local, "mailbox=sent", value)                
            
        elif obj.incoming and not obj.trash:
            value = getattr(_thread_local, "mailbox=inbox", None)
            if not value:
                url = self.get_url_for_callable(
                    parameter_name, 'inbox')
                value = mark_safe(f'<a title="{_("inbox")}" href="{url}">{inbox_icon}</a>')
                setattr(_thread_local, "mailbox=inbox", value)           

        elif not any((obj.incoming, obj.sent, obj.trash)):
            value = getattr(_thread_local, "mailbox=outbox", None)
            if not value:
                url = self.get_url_for_callable(
                    parameter_name, 'outbox')
                value = mark_safe(f'<a title="{_("outbox")}" href="{url}">{outbox_icon}</a>')
                setattr(_thread_local, "mailbox=outbox", value)
                
        elif obj.trash:
            value = getattr(_thread_local, "mailbox=trash", None)
            if not value:
                url = self.get_url_for_callable(
                    parameter_name, 'trash')
                value = mark_safe(f'<a title="{_("trash")}" href="{url}">{trashbox_icon}</a>')
                setattr(_thread_local, "mailbox=trash", value)
                
        return value    # NOQA

    @admin.display(description=_('Content'))
    def readonly_content(self, obj):
        content = obj.content
        if not obj.is_html:
            content = linebreaks(content)
        return mark_safe(
            f'<div style="overflow:auto; width:600px;'
            f' height:200px;">{content}</div>'
        )

    @admin.display(description=_("Previous correspondence"))
    def readonly_prev_corr(self, obj):
        return mark_safe(
            f'<div style="overflow:auto; width:600px;'
            f' height:200px;">{obj.prev_corr}</div>'
        )

    @admin.display(description=signature_str)
    def signature_preview(self, obj):
        if obj.signature:
            return get_signature_preview(obj.signature)
        else:
            return get_signature_preview(_thread_local.signature)

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">today</i>'
    ), ordering='creation_date')
    def the_creation_date(self, obj):
        return obj.creation_date

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
    ), ordering='subject')
    def the_subject(self, obj):
        if not obj.subject:
            obj.subject = _('No subject')
        if obj.inquiry:
            return mark_safe(
                f'<span style="color: var(--green-fg);">{obj.subject}</span>'
            )
        return obj.subject
