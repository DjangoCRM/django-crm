# Generated by Django 5.0.6 on 2024-06-16 18:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('common', '0002_initial'),
        ('crm', '0001_initial'),
        ('massmail', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='crmemail',
            name='signature',
            field=models.ForeignKey(blank=True, help_text="Sender's signature.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner_signature_related', to='massmail.signature', verbose_name='Choose signature'),
        ),
        migrations.AddField(
            model_name='deal',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.city', verbose_name='City'),
        ),
        migrations.AddField(
            model_name='deal',
            name='closing_reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.closingreason', verbose_name='Closing reason'),
        ),
        migrations.AddField(
            model_name='deal',
            name='co_owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_co_owner_related', to=settings.AUTH_USER_MODEL, verbose_name='Co-owner'),
        ),
        migrations.AddField(
            model_name='deal',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='crm.company', verbose_name='Company of contact'),
        ),
        migrations.AddField(
            model_name='deal',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.contact', verbose_name='Contact'),
        ),
        migrations.AddField(
            model_name='deal',
            name='country',
            field=models.ForeignKey(blank=True, help_text='Country', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.country', verbose_name='country'),
        ),
        migrations.AddField(
            model_name='deal',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='deal',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group', verbose_name='Department'),
        ),
        migrations.AddField(
            model_name='deal',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='deal',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner_related', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='deal',
            name='partner_contact',
            field=models.ForeignKey(blank=True, help_text='Contact person of dealer or distribution company', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='partner_contacts', to='crm.contact', verbose_name='Partner contact'),
        ),
        migrations.AddField(
            model_name='crmemail',
            name='deal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deal_emails', to='crm.deal', verbose_name='Deal'),
        ),
        migrations.AddField(
            model_name='industry',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
        migrations.AddField(
            model_name='company',
            name='industry',
            field=models.ManyToManyField(blank=True, to='crm.industry', verbose_name='Industry of company'),
        ),
        migrations.AddField(
            model_name='lead',
            name='city',
            field=models.ForeignKey(blank=True, help_text='Object of City in database', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.city', verbose_name='Company city'),
        ),
        migrations.AddField(
            model_name='lead',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.company', verbose_name='Company of contact'),
        ),
        migrations.AddField(
            model_name='lead',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.contact', verbose_name='Contact'),
        ),
        migrations.AddField(
            model_name='lead',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.country', verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='lead',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group', verbose_name='Department'),
        ),
        migrations.AddField(
            model_name='lead',
            name='industry',
            field=models.ManyToManyField(blank=True, to='crm.industry', verbose_name='Industry of company'),
        ),
        migrations.AddField(
            model_name='lead',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='lead',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner_related', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='lead',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.clienttype', verbose_name='Type of company'),
        ),
        migrations.AddField(
            model_name='deal',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.lead', verbose_name='Lead'),
        ),
        migrations.AddField(
            model_name='crmemail',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lead_emails', to='crm.lead', verbose_name='Lead'),
        ),
        migrations.AddField(
            model_name='leadsource',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.department'),
        ),
        migrations.AddField(
            model_name='lead',
            name='lead_source',
            field=models.ForeignKey(blank=True, help_text='Lead Source', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.leadsource', verbose_name='Lead Source'),
        ),
        migrations.AddField(
            model_name='contact',
            name='lead_source',
            field=models.ForeignKey(blank=True, help_text='Lead Source', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.leadsource'),
        ),
        migrations.AddField(
            model_name='company',
            name='lead_source',
            field=models.ForeignKey(blank=True, help_text='Lead Source', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.leadsource', verbose_name='Lead Source'),
        ),
        migrations.AddField(
            model_name='output',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crm.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='output',
            name='deal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.deal'),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
            ],
            options={
                'verbose_name': 'Shipment',
                'verbose_name_plural': 'Shipments',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('crm.output',),
        ),
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crm.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='payment',
            name='deal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.deal'),
        ),
        migrations.AddField(
            model_name='product',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='product',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group', verbose_name='Department'),
        ),
        migrations.AddField(
            model_name='product',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='output',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.product', verbose_name='Product'),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group', verbose_name='Department'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.productcategory', verbose_name='Product category'),
        ),
        migrations.AddField(
            model_name='rate',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_related', to='crm.currency'),
        ),
        migrations.AddField(
            model_name='request',
            name='city',
            field=models.ForeignKey(blank=True, help_text='Object of City in database', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.city', verbose_name='City'),
        ),
        migrations.AddField(
            model_name='request',
            name='co_owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_co_owner_related', to=settings.AUTH_USER_MODEL, verbose_name='Co-owner'),
        ),
        migrations.AddField(
            model_name='request',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='crm.company', verbose_name='Company of contact'),
        ),
        migrations.AddField(
            model_name='request',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.contact', verbose_name='Contact'),
        ),
        migrations.AddField(
            model_name='request',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.country', verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='request',
            name='deal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='crm.deal', verbose_name='Deal'),
        ),
        migrations.AddField(
            model_name='request',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group', verbose_name='Department'),
        ),
        migrations.AddField(
            model_name='request',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.lead', verbose_name='Lead'),
        ),
        migrations.AddField(
            model_name='request',
            name='lead_source',
            field=models.ForeignKey(blank=True, help_text='Lead Source', null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.leadsource', verbose_name='Lead source'),
        ),
        migrations.AddField(
            model_name='request',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='request',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner_related', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='request',
            name='products',
            field=models.ManyToManyField(blank=True, to='crm.product', verbose_name='Products'),
        ),
        migrations.AddField(
            model_name='deal',
            name='request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='crm.request', verbose_name='Request'),
        ),
        migrations.AddField(
            model_name='crmemail',
            name='request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request_emails', to='crm.request', verbose_name='Request'),
        ),
        migrations.AddField(
            model_name='stage',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group'),
        ),
        migrations.AddField(
            model_name='deal',
            name='stage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.stage', verbose_name='Stage'),
        ),
        migrations.AddField(
            model_name='tag',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_department_related', to='auth.group', verbose_name='Department'),
        ),
        migrations.AddField(
            model_name='tag',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='tag',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner_related', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='lead',
            name='tags',
            field=models.ManyToManyField(blank=True, to='crm.tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='deal',
            name='tags',
            field=models.ManyToManyField(blank=True, to='crm.tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=models.ManyToManyField(blank=True, to='crm.tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='company',
            name='tags',
            field=models.ManyToManyField(blank=True, to='crm.tag', verbose_name='Tags'),
        ),
        migrations.AlterUniqueTogether(
            name='company',
            unique_together={('full_name', 'country')},
        ),
    ]
