# Docker deployment runbook

This guide walks an operator through a **clean-host** installation using the committed
`docker-compose.yml` stack (application, dedicated worker, and private PostgreSQL).

## Operational invariants

The packaged stack guarantees the following unless you deliberately change the compose files:

| Invariant | Detail |
|-----------|--------|
| **Database isolation** | The `db` service has **no published host port**. PostgreSQL is reachable only on the internal `crm_internal` network. |
| **Media access control** | Uploaded media is served **only to authenticated staff** by the application container when `SERVE_MEDIA_FILES=true`. Anonymous users are redirected to login; non-staff users receive HTTP 403. Front the app with a reverse proxy and set `SERVE_MEDIA_FILES=false` if the proxy serves media instead. |
| **Background workloads** | IMAP import, reminders, notifications, and exchange-rate loading run in **exactly one** `worker` container. The `app` service sets `RUN_BACKGROUND_WORKERS=false` and `RUN_INLINE_EMAIL_IMPORT=false`. |

## Prerequisites

- Docker Engine 24+ with the Compose plugin (`docker compose version`)
- Git
- At least 4 GB RAM and 10 GB free disk for images, database, media, and static files
- A host firewall that allows inbound traffic only on the published application port (default `8000`)

Verify tooling:

```bash
docker compose version
git --version
```

## Environment preparation

1. Clone the repository and enter the project root.
2. Copy the environment template — **never commit the resulting `.env` file**:

```bash
cp .env.example .env
```

3. Generate a signing key and paste it into `.env` as `DJANGO_SECRET_KEY`:

```bash
python manage.py generate_secret_key
```

4. Set the minimum compose variables in `.env` using placeholders only:

```bash
DJANGO_SECRET_KEY=<your-django-secret-key>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

POSTGRES_USER=<database-user>
POSTGRES_PASSWORD=<database-password>
POSTGRES_DB=<database-name>
DATABASE_URL=postgresql://<database-user>:<database-password>@db:5432/<database-name>

APP_PUBLISHED_PORT=8000
```

5. Validate configuration (secrets are masked in output):

```bash
python manage.py show_config
```

Optional mail, OAuth, reCAPTCHA, and VoIP variables are documented in `.env.example`. Use placeholders such as `<smtp-password>` — do not embed real credentials in documentation or version control.

## First bring-up

Build and start the stack:

```bash
docker compose up -d --build
```

The entrypoint waits for PostgreSQL, runs migrations and `collectstatic`, then starts Gunicorn on port 8000 inside the `app` container.

Confirm the database port is **not** published:

```bash
docker compose port db 5432
# Expected: error or empty output — port must not be exposed
```

Open the admin login page (default prefix `456-admin`):

```text
http://localhost:8000/456-admin/login/
```

## Seeding reference data

Load committed JSON fixtures via the documented management command:

```bash
docker compose exec app python manage.py setupdata
```

This uses only fixtures shipped in the repository; no external data source is required.

Create an operator superuser when needed:

```bash
docker compose exec app python manage.py createsuperuser
```

## Worker service

The `worker` service runs `docker/worker.sh`, which starts:

- `run_mail_workers` — IMAP manager, import, restore, and inquiry creation
- `run_schedulers` — notification sender, reminders, and exchange-rate loader

The worker shares the `media` volume with the app for lock files. Only **one** worker replica should run.

## Static and media serving

- Static admin assets are collected to `/app/static` and served by WhiteNoise when `DEBUG=false`.
- Media uploads live on the shared `media` volume at `/app/media`.
- Set `SERVE_MEDIA_FILES=false` when a reverse proxy serves media and the app should not expose `/media/` directly.

## Upgrade

1. Pull the target image tag or rebuild from the desired Git revision.
2. Back up the database and media volume (see below).
3. Recreate containers without deleting volumes:

```bash
docker compose pull    # when using published images
docker compose up -d --build
```

Migrations run automatically on app startup when `RUN_MIGRATIONS=1` (default).

## Backup and restore

### Backup

```bash
docker compose exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc > crm-backup.dump
docker run --rm -v django-crm_media:/data -v "$PWD":/backup alpine \
  tar czf /backup/media-backup.tar.gz -C /data .
```

Replace `django-crm_media` with the actual media volume name from `docker volume ls`.

### Restore into a fresh stack

1. Tear down the stack **without** removing volumes if you need in-place recovery, or remove volumes for a clean restore test.
2. Start the stack and wait for PostgreSQL to become healthy.
3. Restore database and media:

```bash
docker compose exec -T db pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists < crm-backup.dump
docker run --rm -v django-crm_media:/data -v "$PWD":/backup alpine \
  tar xzf /backup/media-backup.tar.gz -C /data
```

4. Confirm admin login succeeds at `http://localhost:8000/456-admin/login/`.

The verification script `scripts/compose_verify.sh` automates bring-up, seeding, and optional backup/restore checks.

## Rollback

Reverting to a previous application image tag **does not require data migration reversal**. Application code rolls back independently of PostgreSQL data files and the media volume, provided you have not run irreversible migrations forward-only. To roll back:

1. Check out or pull the previous Git tag.
2. `docker compose up -d --build` using the previous image.
3. If migrations were added in the failed release, restore from backup instead of rolling back schema.

## Troubleshooting

| Symptom / log message | Likely cause | Remediation |
|-----------------------|--------------|-------------|
| `Required configuration variable 'DJANGO_SECRET_KEY' is not set` | Missing mandatory setting in `.env` | Set `DJANGO_SECRET_KEY` using `manage.py generate_secret_key` |
| `Database not ready after N attempts:` | PostgreSQL not healthy or wrong `DATABASE_URL` | Check `docker compose logs db`; verify credentials and `@db` hostname inside compose |
| Migration failure on startup | Schema drift or insufficient DB permissions | Inspect `docker compose logs app`; restore from backup or fix DB user grants |
| `collectstatic` permission error | Static volume not writable by UID 10001 | Ensure `staticfiles` volume is mounted; check ownership under `/app/static` |
| `RuntimeError` / lock timeout under `media/locks` | Multiple worker replicas or stale lock files | Run exactly one worker; clear locks after unclean shutdown |
| PostgreSQL data directory version mismatch | Upgrading major Postgres without dump/restore | Back up with `pg_dump`, recreate `pgdata` volume, restore into matching image tag |
| Admin CSS missing | Static not collected or WhiteNoise misconfigured | Confirm `RUN_COLLECTSTATIC=1`; request `/static/admin/css/base.css` returns 200 |
| Port already allocated | Host port conflict on `APP_PUBLISHED_PORT` | Change `APP_PUBLISHED_PORT` in `.env` |

## Security checklist

- [ ] `.env` is listed in `.gitignore` and never committed
- [ ] `DJANGO_DEBUG=false` in production
- [ ] PostgreSQL port is not published to the host
- [ ] Only the application HTTP port is exposed through the firewall
- [ ] Media is staff-gated or delegated to an authenticated reverse proxy
- [ ] Exactly one worker container runs background workloads

## Automated verification

Maintainers and operators can run the end-to-end check:

```bash
scripts/compose_verify.sh
```

Dry-run (no Docker required — prints the planned sequence):

```bash
scripts/compose_verify.sh --dry-run
```

The script measures wall-clock time from `docker compose up` to a successful admin login response and compares it against `TIME_BUDGET_SECONDS` (default 600 s, excluding image download). Record observed timings for your host in the table below.

### Observed clean-host timing

| Host specification | Image pull excluded | Time-to-ready (seconds) | Date |
|--------------------|--------------------:|------------------------:|------|
| _Run `compose_verify.sh` and paste `TIMING_SUMMARY` output here_ | yes | _pending measurement_ | _YYYY-MM-DD_ |

Target: **under 600 seconds** (10 minutes) after images are cached.
