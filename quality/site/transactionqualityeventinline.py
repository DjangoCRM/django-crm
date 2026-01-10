from django import forms

from crm.site.crmstackedinline import CrmStackedInline
from quality.models import TransactionQualityEvent
from quality.models import TransactionQualitySignal


class QualityEventForm(forms.ModelForm):

    class Meta:
        model = TransactionQualityEvent
        fields = '__all__'
        widgets = {
            'details': forms.Textarea(
                attrs={'cols': 80, 'rows': 2}
            )
        }

    class Media:
        js = (
            '/static/quality/js/update_initial_weight.js',
        )


class TransactionQualityEventInline(CrmStackedInline):
    fieldsets = (
        (None, {
            'fields': (
                ('signal', 'weight'),
                'details',
            )
        }),
    )
    form = QualityEventForm
    icon = '<a id="TransactionQualityEvents"></a><i class="material-icons" style="color: var(--primary-fg)">event</i>'
    model = TransactionQualityEvent
    name_plural = model._meta.verbose_name_plural
    verbose_name_plural = f'{icon} {name_plural}'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "signal":
            kwargs["queryset"] = TransactionQualitySignal.objects.filter(
                department_id=request.user.department_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)