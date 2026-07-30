# Shared Kernel layering contract

`sharedkernel` is the neutral foundation layer for Django-CRM. It exists so
`common`, `crm`, and other apps can share primitives without creating import
cycles.

## Rules

1. **Inbound dependency ban** — `sharedkernel` may import only:
   - the Python standard library
   - Django and other third-party packages
2. **Outbound allowance** — every other project app may import `sharedkernel`.
3. **No domain models** — do not define CRM/task/massmail models here.
4. **No side effects** — `SharedKernelConfig.ready()` must stay empty.

## Modules

| Module | Purpose |
|--------|---------|
| `presentation.py` | Shared formatting constants (future) |
| `adminsites.py` | Admin-site registry hooks (future) |
| `protocols.py` | Cross-app typing protocols (future) |
| `search.py` | Portable audit-log search helpers |
| `credentials.py` | Mailbox credential accessor |

## Verification

Run the layering guard:

```bash
python manage.py test tests.sharedkernel.test_layering
```
