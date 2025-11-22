#!/usr/bin/env python
"""
Script to get Django ContentType IDs for the chat integration.
Run this script to get the correct content type IDs for your database.

Usage:
    python scripts/tmp_rovodev_get_content_types.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType


def get_content_types():
    """Get content type IDs for common CRM models."""
    
    models_to_check = [
        ('crm', 'deal'),
        ('crm', 'contact'),
        ('crm', 'company'),
        ('crm', 'lead'),
        ('tasks', 'task'),
        ('tasks', 'project'),
        ('tasks', 'memo'),
        ('chat', 'chatmessage'),
    ]
    
    print("\n" + "="*70)
    print("Django ContentType IDs for Chat Integration")
    print("="*70 + "\n")
    
    content_type_map = {}
    
    for app_label, model in models_to_check:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
            content_type_map[model] = ct.id
            print(f"✓ {app_label:15} | {model:15} | ID: {ct.id}")
        except ContentType.DoesNotExist:
            print(f"✗ {app_label:15} | {model:15} | NOT FOUND")
    
    print("\n" + "="*70)
    print("JavaScript Content Type Map")
    print("="*70 + "\n")
    
    print("Copy this into frontend/js/chat.js getContentTypeId() method:\n")
    print("const contentTypeMap = {")
    for model, ct_id in content_type_map.items():
        print(f"    '{model}': {ct_id},")
    print("};")
    
    print("\n" + "="*70)
    print("All Available Content Types")
    print("="*70 + "\n")
    
    all_cts = ContentType.objects.all().order_by('app_label', 'model')
    for ct in all_cts:
        print(f"{ct.app_label:20} | {ct.model:20} | ID: {ct.id}")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    get_content_types()
