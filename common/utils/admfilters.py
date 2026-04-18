from django.contrib.admin import SimpleListFilter
from django.db.models import CharField
from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _

from common.models import Department


class ByDepartmentFilter(SimpleListFilter):
    title = _('Department')
    parameter_name = 'user__groups'

    def lookups(self, request, model_admin):
        departments = Department.objects.filter(
            user__groups__isnull=False
        ).distinct().annotate(
            str_id=Cast('id', output_field=CharField())
        ).values_list('str_id', 'name').order_by('name')

        return [*departments]

    def get_facet_counts(self, pk_attname, filtered_qs):
        original_value = self.used_parameters.get(self.parameter_name)
        counts = {}
        for i, choice in enumerate(self.lookup_choices):
            self.used_parameters[self.parameter_name] = choice[0]
            lookup_qs = self.queryset(self.request, filtered_qs)
            if lookup_qs is not None:
                counts[f"{i}__c"] = Count(
                    pk_attname,
                    filter=Q(pk__in=lookup_qs),
                )
        self.used_parameters[self.parameter_name] = original_value
        return counts

    def choices(self, changelist):
        add_facets = changelist.add_facets
        facet_counts = self.get_facet_queryset(
            changelist) if add_facets else None
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('All'),
        }
        for i, (lookup, title) in enumerate(self.lookup_choices):
            if add_facets:
                if (count := facet_counts.get(f"{i}__c", -1)) != -1:
                    title = f"{title} ({count})"
                else:
                    title = f"{title} (-)"
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return queryset

        return queryset.filter(user__groups__id=value)
