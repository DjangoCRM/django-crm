# Layering contract

Django-CRM is organized into four layers. Imports must respect the directions
below. The import-graph gate in `tests/architecture/test_import_graph.py`
enforces this contract on every test run.

## Layers

| Layer | Apps / packages | May import |
| --- | --- | --- |
| **Project shell** | `webcrm`, `settings` | Any lower layer |
| **Feature apps** | `crm`, `tasks`, `massmail`, `analytics`, `chat`, `help`, `quality`, `voip` | `sharedkernel`, `common`, other feature apps when explicitly allow-listed |
| **Common** | `common` | `sharedkernel`, Django/stdlib, `settings`, `webcrm` configuration |
| **Shared kernel** | `sharedkernel` | Django/stdlib only |

## Zero-tolerance core rules

These rules must always have **zero** violations:

1. **`sharedkernel` isolation** — no imports from project apps.
2. **`common` feature isolation** — `common` must not import `crm`, `tasks`,
   `massmail`, `chat`, `help`, `quality`, or `voip`.
3. **`crm` admin isolation** — `crm` must not import `common.admin`.

## Tolerated cross-app coupling

All other cross-app imports must appear in
`tests/architecture/allowed_exceptions_data.json` with a reason and owner.
Adding a new tolerated edge requires updating that file in the same pull request.

## Extension points introduced by REQ-006

| Extension point | Module | Purpose |
| --- | --- | --- |
| Admin-site registry | `sharedkernel.adminsites` | Resolve CRM/admin sites without `common → crm` imports |
| Dashboard counter registry | `sharedkernel.dashboard` | Register app-specific admin index counters |
| Raw-ID label hook | `sharedkernel.admin_labels` / `BaseModelAdmin.raw_id_label_decorator` | Customize raw-id field labels per app |
| Shared inlines | `sharedkernel.inlines` | Reusable admin inlines without circular imports |

## Adding a new shared symbol

1. Place presentation constants in `sharedkernel.presentation`.
2. Place ORM/query helpers in `common.queries`.
3. Place workflow helpers in the appropriate `common.services.*` module.
4. Do **not** add the symbol to `common.utils.helpers` except as a temporary
   shim export with a deprecation mapping (see `docs/adr/helpers-deprecation-shim.md`).
5. Run `python manage.py test tests.architecture.test_import_graph --noinput`
   and update the allow-list if your change introduces a new tolerated edge.

## Fan-in ceiling

Shared modules must not exceed **60** distinct importing files. Current counts
are recorded in `docs/layering-metrics.json`.

Direct imports of symbols relocated out of `common.utils.helpers` must remain
**zero** — use the canonical module listed in the deprecation ADR.

## Verification

```bash
python manage.py test tests.architecture.test_import_graph --noinput
python manage.py test tests.sharedkernel.test_layering --noinput
python manage.py test tests/ --noinput
```

To surface remaining legacy shim usage:

```bash
PYTHONWARNINGS=error::DeprecationWarning python manage.py test tests/ --noinput
```

No production-data fixtures are required for the architecture gate; synthetic
module fixtures live under `tests/architecture/fixtures/import_graph/`.
