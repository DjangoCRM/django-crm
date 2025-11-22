from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_alter_reminder_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='jssip_display_name',
            field=models.CharField(blank=True, default='', help_text='Name shown to the callee', max_length=255, verbose_name='JsSIP display name'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='jssip_sip_password',
            field=models.CharField(blank=True, default='', help_text='Will be used by the web client', max_length=255, verbose_name='JsSIP password'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='jssip_sip_uri',
            field=models.CharField(blank=True, default='', help_text='Example: sip:1001@sip.example.com', max_length=255, verbose_name='JsSIP SIP URI'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='jssip_ws_uri',
            field=models.CharField(blank=True, default='', help_text='Example: wss://sip.example.com:7443', max_length=255, verbose_name='JsSIP WebSocket URI'),
        ),
    ]
