"""Import-order tests for common, chat, and queries modules."""

import os
import subprocess
import sys

from django.test import SimpleTestCase


IMPORT_ORDERS = (
    ('common.models', 'common.queries', 'chat.models'),
    ('chat.models', 'common.models', 'common.queries'),
    ('common.queries', 'chat.models', 'common.models'),
)


class ImportOrderTests(SimpleTestCase):
    def test_import_orders_succeed_in_fresh_interpreter(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        for order in IMPORT_ORDERS:
            with self.subTest(order=order):
                statements = [
                    "import os",
                    "os.environ.setdefault('DJANGO_SECRET_KEY', 'import-order-test-key')",
                    "os.environ.setdefault('DJANGO_DEBUG', 'true')",
                    "os.environ.setdefault('RUN_BACKGROUND_WORKERS', 'false')",
                    "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')",
                    "import django",
                    "django.setup()",
                ]
                statements.extend(f'import {module}' for module in order)
                statements.append("print('ok')")
                result = subprocess.run(
                    [sys.executable, '-c', '; '.join(statements)],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    msg=result.stderr or result.stdout,
                )
