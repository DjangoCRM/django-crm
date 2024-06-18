"""
import os
import json
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.exceptions import ObjectDoesNotExist

file_path = os.path.join(settings.BASE_DIR, 'tests', 'group_perms_data.json')


def export_group_perms():
    # from tests.utils.dump_group_permissions import export_group_perms

    with open(file_path, 'w') as f:
        groups = Group.objects.all()
        data = {}
        for group in groups:
            perms = group.permissions.all()
            data[group.name] = [(p.codename, p.content_type.app_label, p.content_type.model) for p in perms]
        json.dump(data, f, ensure_ascii=False, indent=4)
        
        
def convert_group_fixture():
    # Warning: Should be apply on test base only!
    file_path = os.path.join(settings.BASE_DIR, 'common', 'fixtures', 'groups.json')
    with open(file_path, 'r') as f:
        data = json.load(f)
    for item in data:
        group_name = item["fields"]["name"]
        # try:
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = []
        for p in item["fields"]["permissions"]:
            codename, app_label, model = p
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            perm = Permission.objects.get(
                codename=codename,
                content_type=content_type
            )
            perms.append(perm)
        group.permissions.set(perms)
    management.call_command(
        'dumpdata',
        'auth.Group',
        indent=4,
        output='common/fixtures/groups.json'
    )


def import_group_perms():
    # Warning: Should be apply on test base only!

    with open(file_path, 'r') as f:
        data = json.load(f)
    for group_name, perm_data in data.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = []
        for codename, app_label, model in perm_data:
            content_type = ContentType.objects.get(
                app_label=app_label, model=model
            )
            perm = Permission.objects.get(
                codename=codename,
                content_type=content_type
            )
            perms.append(perm)
        group.permissions.clear()
        group.refresh_from_db()
        group.permissions.set(perms)
    # os.remove(file_path)

    management.call_command(
        'dumpdata',
        'auth.Group',
        indent=4,
        output='common/fixtures/groups.json'
    )
"""