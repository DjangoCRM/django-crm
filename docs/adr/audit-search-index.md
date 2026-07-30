# ADR: Audit search index strategy for `django_admin_log`

## Status

Accepted — implemented in `common/migrations/0006_logentry_audit_indexes.py`.

## Context

WO-024 moves `LogEntryAdmin.get_search_results` to database-side filtering. The
`django.contrib.admin.models.LogEntry` table (`django_admin_log`) is owned by
Django's built-in `admin` app. Attempting `AddIndex` on `admin.LogEntry` from a
`common` app migration raises:

```text
ValueError: Indexes defined in a migration must be defined in the same app as the model.
```

Additionally, `change_message` is a `TextField`. MySQL InnoDB cannot index full
TEXT columns without a prefix length, which violates the portable-model rule in
`crm/models/README.md`.

## Options considered

| Option | Outcome |
|--------|---------|
| AddIndex from `common` on `admin.LogEntry` | **Rejected** — Django app ownership error (see above). |
| `MIGRATION_MODULES` redirection for `admin` | **Rejected** — high upgrade hazard; must vendor upstream admin migrations. |
| Prefix index on `change_message` (MySQL) | **Rejected** — vendor-specific prefix length syntax. |
| Index portable fixed-width columns only | **Accepted** — bounds scans; text matching uses `change_message__contains`. |

## Decision

Add explicitly named indexes on portable columns via `RunPython` +
`schema_editor.add_index` against `admin.LogEntry`:

- `crm_audit_log_object_id_idx` — `object_id`
- `crm_audit_log_action_time_idx` — `action_time`
- `crm_audit_log_user_id_idx` — `user_id`
- `crm_audit_log_content_type_id_idx` — `content_type_id`

`change_message` is **not** indexed. Text search relies on filtered scans bounded
by the indexed lookup columns (notably the ID-prefix branch on `object_id`).

## Rollback

Reverse migration drops the four indexes by name. Safe on SQLite, PostgreSQL,
and MySQL because no data migration is involved.

```bash
python manage.py migrate common 0005_userprofile_avatar
python manage.py migrate common 0006_logentry_audit_indexes
```

## Verification

- `tests/common/test_logentry_audit_indexes.py` introspects constraints after migrate.
- WO-021 parity harness and WO-022 service tests must pass unchanged after indexing.
