from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import Base1


class BasePriceRule(models.Model):
    class Meta:
        abstract = True

    price_type_choices = {
        'F': _('Fixed Price'),
        'D': _('Discount percentage'),
        'M': _('Markup percentage')
    }
    price_type = models.CharField(
        max_length=1, choices=price_type_choices,
        verbose_name=_("Price type")
    )
    tier_name = models.ForeignKey(
        "crm.ClientType",
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_tier_name_related",
        verbose_name=_("Name"),
    )
    base_tier = models.BooleanField(
        default=False,
        verbose_name=_("Base tier"),
        help_text=_(
            "Indicates whether this price level is the base tier for calculating other tiers in the department.")
    )
    percentage = models.DecimalField(
        blank=True, null=True, max_digits=5, decimal_places=2,
        verbose_name=_("Percentage"),
        help_text=_(
            "The percentage of discount or markup relative to the base tier.")
    )
    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Update date")
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_modified_by_related",
        verbose_name=_("Modified By")
    )

    def __str__(self):
        return str(self.tier_name).upper()


class CategoryPriceRule(BasePriceRule):
    """
    Model representing category-specific pricing rule.
    """

    class Meta:
        verbose_name = _("Category Price Rule")
        verbose_name_plural = _("Category Price Rules")
        unique_together = ["tier_name", "category"]

    category = models.ForeignKey(
        "crm.ProductCategory",
        blank=False, null=False,
        on_delete=models.CASCADE,
        verbose_name=_("Product Category"),
        related_name="%(app_label)s_%(class)s_category_related",
    )


class DepartmentPriceRule(BasePriceRule):
    """
    Model representing department-specific pricing rule.
    """

    class Meta:
        verbose_name = _("Department Price Rule")
        verbose_name_plural = _("Department Price Rules")
        unique_together = ["tier_name", "department"]

    department = models.ForeignKey(
        'auth.Group',
        blank=False, null=False,
        on_delete=models.CASCADE,
        verbose_name=_("Department"),
        related_name="%(app_label)s_%(class)s_department_related",
    )


class ProductPriceTier(Base1):
    class Meta:
        verbose_name = _("Product Price Tier")
        verbose_name_plural = _("Product Price Tiers")
        unique_together = ["tier_name", "product"]

    tier_name = models.ForeignKey(
        "crm.ClientType",
        blank=False, null=False,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_tier_name_related",
        verbose_name=_("Tier Name")
    )
    price = models.DecimalField(
        blank=False, null=False, max_digits=10, decimal_places=2,
        verbose_name=_("Price")
    )
    description = models.TextField(
        blank=True, default='',
        verbose_name=_("Description"),
    )
    product = models.ForeignKey(
        'Product', blank=False, null=False, on_delete=models.CASCADE,
        verbose_name=_("Product")
    )
    min_quantity = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Minimum Quantity")
    )
    valid_from = models.DateField(
        blank=True, null=True,
        verbose_name=_("Valid From")
    )
    valid_to = models.DateField(
        blank=True, null=True,
        verbose_name=_("Valid To")
    )

    def __str__(self):
        return str(self.tier_name)


CategoryPricingTier = CategoryPriceRule
DepartmentPricingTier = DepartmentPriceRule
TieredPricingRule = ProductPriceTier
