from django.contrib.auth import get_permission_codename
from django.utils.translation import gettext_lazy as _
from django import forms
from crm.forms.admin_forms import TagForm
from crm.site.crmmodeladmin import CrmModelAdmin


class TagAdmin(CrmModelAdmin):
    form = TagForm
    list_display = ('name',)
    readonly_fields = (
        'owner',
        'modified_by',
        'creation_date',
        'update_date'
    )
    save_on_top = False

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': ('name',)
            }),
            (_('Additional information'), {
                'classes': ('collapse',) if request.user.department_id else (),
                'fields': (
                    ('owner', 'modified_by'),
                    ('creation_date', 'update_date'),
                    'department'
                )
            }),
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            kwargs["initial"] = request.user.department_id

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_form(self, request, obj=None, **kwargs):
     form = super().get_form(request, obj=None, **kwargs)
     if not request.user.department_id:
        form.base_fields['department'].widget = forms.Select()
        form.base_fields['department'].required = True
     return form

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        
        opts = self.opts
        codename = get_permission_codename("change", opts)
        value = request.user.has_perm("%s.%s" % (opts.app_label, codename))
        if not value or not obj:
            return value
        if obj.department_id == request.user.department_id:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
