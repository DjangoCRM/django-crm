from django.db import migrations, models


INDEX_DEFINITIONS = (
    models.Index(fields=['object_id'], name='crm_audit_log_object_id_idx'),
    models.Index(fields=['action_time'], name='crm_audit_log_action_time_idx'),
    models.Index(fields=['user_id'], name='crm_audit_log_user_id_idx'),
    models.Index(
        fields=['content_type_id'],
        name='crm_audit_log_content_type_id_idx',
    ),
)


def add_logentry_indexes(apps, schema_editor):
    log_entry = apps.get_model('admin', 'LogEntry')
    for index in INDEX_DEFINITIONS:
        schema_editor.add_index(log_entry, index)


def remove_logentry_indexes(apps, schema_editor):
    log_entry = apps.get_model('admin', 'LogEntry')
    for index in INDEX_DEFINITIONS:
        schema_editor.remove_index(log_entry, index)


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('common', '0005_userprofile_avatar'),
    ]

    operations = [
        migrations.RunPython(
            add_logentry_indexes,
            remove_logentry_indexes,
        ),
    ]
