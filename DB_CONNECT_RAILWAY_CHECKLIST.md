# Railway DB connectivity checklist (for MindBloomV2)

## Symptom
Backend deploy fails with:
- `Can't connect to MySQL server on 'mysql.railway.internal' ([Errno -2] Name or service not known)`

## Root cause
`mysql.railway.internal` is not resolvable/reachable from the backend container. The DB host/URL you set is not the application-reachable host.

## Fix options (pick one)

### Option A (recommended): use `DATABASE_URL`
1) In **Railway backend service** environment variables, set:
   - `DATABASE_URL` = the full value Railway provides for *application* connections.
2) Redeploy backend.
3) Do not use `MYSQL_HOST` / `MYSQLUSER` / `MYSQLPASSWORD` unless you need to override.

### Option B: use split `MYSQL_*` vars
In **Railway backend service** env vars, set exactly:
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`

Important:
- `MYSQL_HOST` must be the hostname that is resolvable from the backend container.
- Do NOT set `MYSQL_HOST=mysql.railway.internal` unless Railway explicitly says it is reachable for app access.

## Which variables to add (quick mapping)
- If using `DATABASE_URL` ⇒ add ONLY `DATABASE_URL` (plus unrelated app vars).
- If using split vars ⇒ add ONLY the 5 `MYSQL_*` vars listed above.

## Verify
After redeploy:
- Backend should not crash during `python manage.py bootstrap_db`.
- Frontend 502 should disappear after backend is reachable.

