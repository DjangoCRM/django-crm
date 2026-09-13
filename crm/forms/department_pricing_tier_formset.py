from django import forms
from django.utils.translation import gettext as _

from crm.models.pricingtier import DepartmentPriceRule


class DepartmentPriceRuleFormSet(forms.BaseInlineFormSet):
    model = DepartmentPriceRule

    def clean(self):
        super().clean()
        forms_data = [
            form
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get("DELETE", False)
        ]
        base_forms = [
            form
            for form in forms_data
            if form.cleaned_data.get("base_tier")
        ]
        # Validate that the base_tier is one for the department
        if len(base_forms) > 1:
            for form in base_forms:
                add_error_if_changed(
                    form,
                    "base_tier",
                    _("There can only be one base tier for the department.")
                )
        # Validate that the percentage is set for non-base tiers or non-fixed price types.
        # The base level price type is always fixed type.
        non_base_forms = [
            form
            for form in forms_data
            if not form.cleaned_data.get("base_tier")
        ]

        for form in non_base_forms:
            percentage = form.cleaned_data.get("percentage")
            price_type = form.cleaned_data.get("price_type")

            if not percentage and price_type != "F":
                add_error_if_changed(
                    form,
                    "percentage",
                    _("Percentage must be set for non-base tiers.")
                )

        # Validate that the price_type value is the same for all department tiers (except base).
        price_types = {
            form.cleaned_data.get("price_type")
            for form in non_base_forms
            if form.cleaned_data.get("price_type") is not None
        }

        if len(price_types) > 1:
            for form in non_base_forms:
                add_error_if_changed(
                    form,
                    "price_type",
                    _(
                        "All non-base tiers must have the same price type."
                    )
                )


def add_error_if_changed(form, field, message):
    if field in form.changed_data:
        form.add_error(field, message)
