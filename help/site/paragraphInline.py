from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils import translation
from django.utils.safestring import mark_safe

from help.models import Paragraph


class ParagraphInlineForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        

class ParagraphInline(admin.StackedInline):
    extra = 0
    empty_value_display = ""
    fields = ['safe_content', 'links']
    form = ParagraphInlineForm
    model = Paragraph
    readonly_fields = ('content', 'safe_content', 'links')
    template = "admin/help/stacked.html"

    # -- ModelAdmin methods -- #

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            obj_id = request.resolver_match.kwargs['object_id']
            q_params = Q(language_code=translation.get_language())
            q_params &= Q(document_id=obj_id) & Q(draft=False)
            if not request.user.is_superuser:
                user_groups = request.user.groups.all()
                q_params &= Q(groups__in=user_groups)
            qs2 = qs.filter(q_params)
            if qs2:
                return qs2
        except KeyError:
            pass
        return qs
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True    
    
    # -- ModelAdmin Callables -- #
    
    @admin.display(description='')
    def safe_content(self, obj):
        html = obj.content.replace(
            'SECRET_CRM_PREFIX/',
            settings.SECRET_CRM_PREFIX
        )
        return mark_safe(html)

    @admin.display(description='')
    def links(self, obj):
        paragraph = Paragraph.objects.get(id=obj.link1_id)
        anchor = f"#paragraph-{paragraph.id}"
        page_id = paragraph.document_id
        url = reverse("site:help_page_change", args=(page_id,))
        title = paragraph.title
        return mark_safe(
            f'<a href={url + anchor}>{title}</a>'
        )
