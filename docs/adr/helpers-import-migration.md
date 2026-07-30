# Helper import migration (WO-033)

Internal modules now import relocated symbols from their canonical modules instead of
`common.utils.helpers`. The mapping matches `docs/adr/helpers-deprecation-shim.md`.

Only `USER_MODEL` continues to import from `common.utils.helpers` where needed. Historical
Django migrations still reference `common.utils.helpers.token_default` and were not modified.

Codemod: `scripts/migrate_helper_imports.py` (one symbol per import line, in-place replacement).
