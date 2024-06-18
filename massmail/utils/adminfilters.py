from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _


class StatusMailingFilter(SimpleListFilter):
    title = _('Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('A', _('Active')),
            ('P', _('Paused')),
            ('I', _('Interrupted')),
            ('D', _('Done')),
        )
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'A':
            return queryset.filter(status__in=('A', 'E'))
        if self.value() == 'P':
            return queryset.filter(status='P')
        if self.value() == 'I':
            return queryset.filter(status='I')
        if self.value() == 'D':
            return queryset.filter(status='D')

