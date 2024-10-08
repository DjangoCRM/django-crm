# Generated by Django 5.1 on 2024-09-05 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_interval', models.PositiveBigIntegerField(default='300', help_text="Specify the interval in seconds to check if it's time for a reminder.", verbose_name='Check interval')),
            ],
            options={
                'verbose_name': 'Reminder settings',
                'verbose_name_plural': 'Reminder settings',
            },
        ),
    ]
