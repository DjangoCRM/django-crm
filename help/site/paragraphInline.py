from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.utils import translation
from django.utils.safestring import mark_safe

from help.models import Paragraph


class ParagraphInlineForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        

class ParagraphInline(admin.StackedInline):
    extra = 0
    fields = ('html',)
    form = ParagraphInlineForm
    model = Paragraph
    readonly_fields = ('content', 'html')
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
    def html(self, obj):
        html = obj.content.replace(
            'SECRET_CRM_PREFIX/',
            settings.SECRET_CRM_PREFIX
        )
        return mark_safe(html)
