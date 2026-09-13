from django.contrib import admin
from django.utils.translation import gettext as _

from common.utils.helpers import LEADERS
from crm.models.pricingtier import CategoryPriceRule, ProductPriceTier
from crm.site.crmstackedinline import CrmStackedInline
from crm.models.pricingtier import DepartmentPriceRule
from common.models import Department


class ProductPriceTierInline(CrmStackedInline):
    fieldsets = [
        (None, {
            'fields': (
                ('tier_name', 'show_price_type'),
                ('price', 'show_currency'),
            )
        }),
        (_("Additional information"), {
            "classes": ["collapse"],
            'fields': (
                'min_quantity', ('valid_from', 'valid_to'), 'description',
                ('update_date', 'modified_by')
            )
        })
    ]
    ordering = ["-price"]
    model = ProductPriceTier
    readonly_fields = ('show_price_type', 'show_currency',
                       'update_date', 'modified_by')

    # -- ModelAdmin methods -- #

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        if self.opts.auto_created:
            return self._has_any_perms_for_target_model(request, ["change"])
        return super().has_change_permission(request)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if obj:
            category_rules = (
                CategoryPriceRule.objects.filter(
                    category_id=obj.product_category_id
                )
                if obj.product_category_id
                else CategoryPriceRule.objects.none()
            )

            # Category rules take precedence over department rules.
            price_rules = (
                category_rules
                if category_rules.exists()
                else DepartmentPriceRule.objects.filter(
                    department_id=obj.department_id
                )
            )
            if ProductPriceTier.objects.filter(product=obj).exists():
                available_price_tiers = price_rules
            else:
                available_price_tiers = price_rules.filter(base_tier=True)
            choices = [
                (price_rule.tier_name.id, str(price_rule.tier_name))
                for price_rule in available_price_tiers
            ]
            formset.form.base_fields['tier_name'].choices = choices
        return formset

    # -- ModelAdmin Callables -- #

    @admin.display(description=_('Currency'))
    def show_currency(self, obj):
        if obj.pk:
            return Department.objects.get(pk=obj.product.department_id).default_currency
        return LEADERS

    @admin.display(description=_('Price type'))
    def show_price_type(self, obj):
        if obj.pk:
            product = obj.product
            tier_name = obj.tier_name

            if product.product_category_id:
                price_rule = CategoryPriceRule.objects.filter(
                    category_id=product.product_category_id,
                    tier_name=tier_name,
                ).first()
            else:
                price_rule = None
            if not price_rule:
                price_rule = DepartmentPriceRule.objects.filter(
                    department_id=product.department_id,
                    tier_name=tier_name,
                ).first()
            if price_rule:
                return DepartmentPriceRule.price_type_choices.get(price_rule.price_type, '')
        return ''
