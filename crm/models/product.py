from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from common.models import Base1


class ProductCategory(Base1):
    class Meta:
        verbose_name = _("Product category")
        verbose_name_plural = _("Product categories")
        ordering = ['name']

    name = models.CharField(
        max_length=70, default='', blank=False,
        verbose_name=_("Name")
        )
    description = models.TextField(
        blank=True, default='',
        verbose_name=_("Description"),
    )
    owner = None

    modified_by = None
    
    def __str__(self):
        return self.name


class Product(Base1):
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']
        
    name = models.CharField(
        max_length=70, default='', blank=False,
        verbose_name=_("Name") 
        )    
    description = models.TextField(
        blank=True, default='',
        verbose_name=_("Description"),
    )
    price = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2,
        verbose_name=_("Price")
    )
    currency = models.ForeignKey(
        'Currency', blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("Currency")
    )         
    owner = None
    files = GenericRelation('common.TheFile')
    on_sale = models.BooleanField(
        default=True,
        verbose_name=_("On sale")
    )
    TYPE_CHOICES = (
        ('G', _('Goods')),
        ('S', _('Service'))
    )
    type = models.CharField(
        null=True,
        max_length=1, choices=TYPE_CHOICES, default='G',
        verbose_name=_("Type"),
    )
    product_category = models.ForeignKey(
        'ProductCategory', blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Product category")
    )

    def __str__(self):
        return self.name
