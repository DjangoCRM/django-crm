# Generated manually for request case field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0008_company_district_company_region_contact_district_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='case',
            field=models.BooleanField(default=False, help_text='A request that does not involve payment', verbose_name='Case/Incident'),
        ),
    ]
