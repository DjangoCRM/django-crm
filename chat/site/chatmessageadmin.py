import threading
from urllib.parse import urlencode
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Case
from django.db.models import BooleanField
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models import When
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import Least
from django.template import loader
from django.template.defaultfilters import linebreaks
from django.http import HttpResponseRedirect
from django.http import QueryDict
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.urls import reverse

from chat.forms.chatmessageform import ChatMessageForm
from chat.models import ChatMessage
from common.models import UserProfile
from crm.models import Deal
from common.admin import FileInline
from common.utils.helpers import CRM_NOTICE
from common.utils.helpers import get_trans_for_user
from common.utils.helpers import LEADERS
from common.utils.helpers import send_crm_email
from common.utils.helpers import USER_MODEL
from common.utils.helpers import save_message
from tasks.models import Memo
from tasks.models import Project
from tasks.models import Task

_thread_local = threading.local()
download_icon = '<i class="material-icons" ' \
                'style="font-size:17px;vertical-align:middle;">file_download</i> '
red_download_icon = '<i class="material-icons" ' \
                    'style="font-size:17px;vertical-align:middle;color: var(--error-fg);">file_download</i>'
error_outline_icon = '<i class="material-icons" ' \
                     'style="font-size:17px;vertical-align:middle;color: var(--error-fg)">error_outline</i>'
recipients_title_str = _('recipients')
file_error = f'<span style="color: var(--error-fg)">{_("Error: the file is missing.")}</span>'
today_icon = '<i class="material-icons" title="Creation date" style="color: var(--body-quiet-color)">today</i>'
task_operator_str = _("task operator")
you_rcvd_msg_str = _("You received a message regarding - ")
crm_prefix = _(settings.EMAIL_SUBJECT_PREFIX)


class ChatMessageAdmin(admin.ModelAdmin):
    form = ChatMessageForm
    list_display = (
        'envelope', 'message', 'person', 'recipient_list',
        'reply', 'files', 'created', 'id'
    )
    list_display_links = ('message',)
    raw_id_fields = (
        'content_type', 'answer_to', 'topic', 'owner'
    )
    readonly_fields = (
        'envelope', 'message', 'reply', 'reply_to_message', 'files'
    )
    actions = ['delete_selected']
    search_fields = ('content',)
    inlines = [FileInline]

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        initial = dict(request.GET.items())
        if initial.get('content_type__id__exact', None):
            extra_context['content_type_id'] = int(
                initial.get('content_type__id__exact'))
            extra_context['object_id'] = int(initial.get('object_id'))
            ct = ContentType.objects.get(id=extra_context['content_type_id'])
            extra_context['view_button_url'] = reverse(
                f'site:{ct.app_label}_{ct.model}_change', args=(extra_context['object_id'],)
            )
            extra_context['view_button_title'] = f"{gettext('View')} - {gettext(f'{ct}')}"
        return super().changelist_view(request, extra_context)

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        id_list = []
        for msg in cl.result_list.filter(recipients=request.user):
            msg.recipients.remove(request.user.id)
            id_list.append(msg.id)
        cl.result_list = cl.result_list.annotate(
            top_id=Coalesce('topic_id', 'id'),
            date=Least(
                Coalesce('topic_id__creation_date', 'creation_date'),
                'creation_date'
            ),
            is_unread=Case(
                When(id__in=id_list, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
        ).order_by('-date', 'top_id', 'id')
        return cl

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {'fields': [
                'content',
                'content_type',
                'object_id',
                'answer_to',
                'topic',
                'owner',
                'to'
            ]})
        ]
        if 'answer_to' in request.GET:
            answer_to = int(request.GET.get('answer_to'))
            msg = self.model.objects.get(id=answer_to)
            _thread_local.reply_to_message = msg.content
            fieldsets[0][1]['fields'].insert(0, 'reply_to_message')
            fieldsets.append((_('Additional information'), {
                # 'classes': ('collapse',),
                'fields': ['recipients']
            }))
        else:
            fieldsets[0][1]['fields'].append('recipients')
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['recipients'] = MyModelMultipleChoiceField(
            queryset=get_recipients_queryset(request),
            required=True,
            widget=FilteredSelectMultiple(_("Recipients"), False, ),
        )
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        initial = dict(request.GET.items())
        if '_changelist_filters' in initial:
            initial = QueryDict(initial['_changelist_filters']).dict()
        qs = qs.filter(**initial)
        if not any((request.user.is_superuser, request.user.is_chief)):
            qs = qs.filter(
                Q(owner_id=request.user.id) |
                Q(to=request.user.id)
            ).distinct()
        return qs

    def response_add(self, request, obj, post_url_continue=None):
        if obj.answer_to:
            obj.answer_to.recipients.remove(request.user.id)
        if '_popup' in request.POST:
            return HttpResponse('<script type="text/javascript">window.close()</script>')
        return self.redirect_to_changelist(obj)

    def response_change(self, request, obj):
        if '_popup' in request.POST:
            return HttpResponse(
                '<script type="text/javascript">window.close()</script>'
            )
        return self.redirect_to_changelist(obj)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        content_obj = obj.content_object
        content_obj_name = content_obj._meta.verbose_name  # NOQA
        subject = f"{crm_prefix}{you_rcvd_msg_str} {content_obj_name}: {content_obj}"
        subject = " ".join(subject.splitlines())
        params = {
            'content_type__id__exact': obj.content_type_id,
            'object_id': obj.object_id
        }
        url = reverse(
            'site:chat_chatmessage_changelist'
        ) + f'?{urlencode(params)}'
        recipient_list = []
        recipients = obj.recipients.all()
        for user in recipients:
            regarding = get_trans_for_user("regarding - ", user)
            you_received = get_trans_for_user("You received a ", user)
            save_message(
                user,
                f'{CRM_NOTICE} {you_received}<a href="{url}"> '
                f'{get_trans_for_user("message", user)}'
                f'</a> {regarding}{content_obj_name}: {content_obj}',
                'INFO'
            )
            if getattr(user, 'email'):
                recipient_list.append(user.email)
        if recipient_list:
            query_str = get_query_string(obj)
            reply_url = reverse(
                'site:chat_chatmessage_add'
            ) + f'?{query_str}'
            content_obj_url = request.build_absolute_uri(
                content_obj.get_absolute_url()
            )

            template = loader.get_template("chat/chatmessage_email.html")
            site = Site.objects.get_current()
            context = {
                'obj': obj,
                'message': self.message(obj),
                'domain': site.domain,
                'regarding': regarding.capitalize(),
                'content_obj_name': content_obj_name,
                'content_obj_url': content_obj_url,
                'content_obj': content_obj,
                'absolute_uri': request.build_absolute_uri(reply_url)
            }
            html_message = template.render(context)
            send_crm_email(subject, html_message, recipient_list)

    # -- ModelAdmin callables -- #

    @admin.display(description='')
    def envelope(self, instance):
        icon = '<i class="material-icons" title="Edit message" style="color: var(--body-quiet-color)">drafts</i>'
        if getattr(instance, 'is_unread', None):
            icon = '<i class="material-icons" title="Edit message" style="color: var(--body-quiet-color)">mail</i>'
        if instance.answer_to:
            return mark_safe(
                f'<span style="margin-left:30px;display:block;">{icon}</span>'
            )
        return mark_safe(icon)

    @staticmethod
    def files(obj):
        files = FileInline.model.objects.filter(chat_message=obj)
        if files:
            for f in files:
                file = getattr(f, 'file', None)
                if file:
                    file_links = f'{download_icon} <a href="{file.url}">{f}</a><br>'
                else:
                    file_links = f'{red_download_icon}{error_outline_icon} {file_error}'
            return mark_safe(file_links)  # NOQA
        return ''

    @staticmethod
    def message(obj):
        if obj.content:
            text = linebreaks(obj.content)
            if getattr(obj, 'is_unread', None):
                text = f'<span style="font-weight:bold;font-size:120%;">{text}</span>'
            if not obj.answer_to:
                return mark_safe(f'<span style="font-weight:normal;font-size:120%;">{text}</span>', )
            return mark_safe(
                f'<span style="font-weight:normal;font-size:120%;margin-left:30px;display:block;">{text}</span>'
            )
        return LEADERS

    @admin.display(description=mark_safe(
        f'<a title="{recipients_title_str}">'
        '<i class="material-icons" style="color: '
        'var(--body-quiet-color)">people_outline</i></a>'
    ))
    def recipient_list(self, obj):
        return mark_safe(
            f'{", ".join([str(u) for u in obj.to.all()])}'
        )

    @admin.display(description=mark_safe(
        f'<ul class="object-tools" style="margin-top:0px;">{_("reply")}</ul>'
    ))
    def reply(self, obj):
        """REPLY button in changelist view"""
        title = gettext("reply")
        query_str = get_query_string(obj)
        reply_url = reverse('site:chat_chatmessage_add') + \
            f'?{query_str}&_popup=1'
        my_window = f"window.open('{reply_url}','reply{obj.id}','width=800,height=700');return false;"
        li = f'<li><a  href="#" onClick="{my_window}">{title}</a></li>'
        return mark_safe(
            f'<ul class="object-tools" style="margin-top:0px;">{li}</ul>'
        )

    @admin.display(description=_('Reply to'))
    def reply_to_message(self, obj):  # NOQA
        return getattr(_thread_local, 'reply_to_message', None)

    @admin.display(description=mark_safe(today_icon),
                   ordering='creation_date')
    def created(self, obj):
        return obj.creation_date.date()

    @admin.display(description=mark_safe(
        '<i class="material-icons" title="Owner" style="color: var(--body-quiet-color)">person</i>'
    ), ordering='owner')
    def person(self, obj):
        if getattr(obj, 'co_owner', None):
            return f'{obj.owner}, {obj.co_owner}'
        else:
            return obj.owner

    # -- Custom methods -- #

    @staticmethod
    def redirect_to_changelist(obj):
        params = {
            'content_type__id__exact': obj.content_type_id,
            'object_id': obj.object_id
        }
        return HttpResponseRedirect(reverse(
            "site:chat_chatmessage_changelist") + f'?{urlencode(params)}'
        )


def get_recipients_queryset(request: WSGIRequest) -> QuerySet:
    initial = dict(request.GET.items())
    if initial.get('answer_to', None):
        answer_to_id = int(initial['answer_to'])
        msg = ChatMessage.objects.get(id=answer_to_id)
        ids = msg.to.exclude(id=request.user.id).values_list('id', flat=True)
        ids = list(ids)
        ids.append(msg.owner_id)
        return USER_MODEL.objects.filter(
            id__in=ids
        )

    if initial.get('content_type', None):
        content_type_id = int(initial['content_type'])
        object_id = int(initial['object_id'])
    elif initial.get('_changelist_filters', None):
        changelist_filters = initial['_changelist_filters']
        data = changelist_filters.split('&')
        content_type_id = int(data[0].lstrip('content_type__id__exact='))
        object_id = int(data[1].lstrip('object_id='))
    else:
        obj_id = request.resolver_match.kwargs['object_id']
        msg = ChatMessage.objects.get(id=obj_id)
        content_type_id = msg.content_type_id
        object_id = msg.object_id
    content_type = ContentType.objects.get(pk=content_type_id)
    content_object = content_type.get_object_for_this_type(pk=object_id)
    if content_object.__class__ == Deal:
        id_list = [content_object.owner_id, content_object.co_owner_id]
        head = USER_MODEL.objects.filter(
            groups=content_object.department
        ).filter(groups__name='department heads').first()
        if head:
            id_list.append(head.id)
    elif content_object.__class__ == Task:
        id_list = [
            content_object.owner_id,
            content_object.co_owner_id,
            *list(content_object.responsible.values_list('id', flat=True)),
            *list(content_object.subscribers.values_list('id', flat=True))
        ]
        if content_object.task:
            id_list.extend([
                *list(content_object.task.responsible.values_list('id', flat=True)),
                *list(content_object.task.subscribers.values_list('id', flat=True))
            ])
    elif content_object.__class__ == Project:
        id_list = [
            content_object.owner_id,
            content_object.co_owner_id,
            *list(content_object.responsible.values_list('id', flat=True)),
            *list(content_object.subscribers.values_list('id', flat=True))
        ]
    elif content_object.__class__ == Memo:
        id_list = [
            content_object.owner_id,
            content_object.to_id
        ]
    elif content_object.__class__ == UserProfile:
        id_list = [content_object.pk]

    q_params = Q(id__in=id_list)  # NOQA
    if content_object.__class__ != UserProfile:
        q_params |= Q(groups__name='chiefs')
    if content_object.__class__ in (Task, Memo, Project):
        q_params |= Q(groups__name='task_operators')
    recipients_queryset = USER_MODEL.objects.filter(
        q_params
    ).distinct()

    return recipients_queryset.exclude(id=request.user.id)


def get_query_string(obj: ChatMessage) -> str:
    """Used to form a query string for a 'Reply' link"""
    params = {
        'answer_to': obj.id,
        'recipients': obj.owner.id,
        'content_type': obj.content_type_id,
        'object_id': obj.object_id
    }
    if obj.answer_to:
        if obj.answer_to.topic:
            params['topic'] = obj.answer_to.topic.id
        else:
            params['topic'] = obj.answer_to.id
    else:
        params['topic'] = obj.id
    recipients = obj.recipients.all()
    if len(recipients) == 1:
        params['owner'] = recipients.first().id
    return urlencode(params)


class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        if obj.groups.filter(name='task_operators').exists():
            return f"{obj.username} ({task_operator_str})"
        return obj.username
