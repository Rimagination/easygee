# Quota Monitoring

Use this reference when the user asks to show Earth Engine quota values, sends a
Cloud Console quota URL, or asks whether a quota/project is ready for larger
GEE/geemap work.

## Standard Flow

For new one-sentence geemap/GEE authorization, prefer solving quota readiness
inside the auth runner first:

```powershell
python scripts/authorize_geemap_once.py --project PROJECT_ID --run --quota-mode required
```

This makes missing `gcloud`, Cloud Quotas permission, or Monitoring permission
an authorization/setup result instead of a later browser UI surprise.

If the task is only to prepare Google Cloud CLI, use the fixed resource helper:

```powershell
python scripts/ensure_gcloud_cli.py --project PROJECT_ID --run
```

On Windows, EasyGEE treats `%LOCALAPPDATA%\EasyGEE\tools\google-cloud-sdk` as the reusable
Google Cloud CLI resource and prefers the bundled-Python archive so direct
`gcloud.cmd` calls work without relying on PATH. `EASYGEE_GCLOUD` can point to
an exact `gcloud` binary, and `EASYGEE_GCLOUD_ROOT` can point to another fixed
SDK directory.

1. Parse the Cloud project from `project=` in the Console URL, or ask for the
   Project ID if it is missing.
2. Run the quota helper:

```powershell
python scripts/show_ee_quotas.py "https://console.cloud.google.com/iam-admin/quotas?service=earthengine.googleapis.com&project=PROJECT_ID"
python scripts/show_ee_quotas.py --project PROJECT_ID
python scripts/show_ee_quotas.py --project PROJECT_ID --include-usage
```

3. Report whether the table came from live Cloud Quotas/gcloud data or from the
   official Earth Engine default/fixed quota reference.
4. Never request or print OAuth tokens, service account keys, credential files,
   browser auth URLs, or `gcloud auth print-access-token` output.

## What The Helper Shows

- **Live quota values**: reads `QuotaInfo` rows for
  `earthengine.googleapis.com` through `gcloud beta quotas info list` or the
  Cloud Quotas REST API.
- **Recent usage**: optional `--include-usage` asks Cloud Monitoring for recent
  consumer-quota usage metrics. This may return no rows if the project has no
  recorded usage for the window or the caller lacks Monitoring permissions.
- **Fallback reference**: if live access is unavailable, prints official Earth
  Engine default and fixed quota values plus the exact Console URL.

Cloud Quotas and gcloud usually show the configured **limit values**. Current
usage/usage percentage is a Monitoring concern and may need
`monitoring.timeSeries.list`.

Cloud Quotas can return a very large signed integer for a quota that the Cloud
Console renders as `Unlimited`. EasyGEE normalizes this to `Unlimited` before
computing percentages. Do not treat the raw max-int value as an actual amount
of available EECU-time.

When Cloud Monitoring returns some Earth Engine usage rows but a specific quota
metric is absent, treat that metric as **zero recent usage in the selected
window**, not as an authorization failure. For example, a project that has not
used BigQuery raster functions may show a live
`earthengine.googleapis.com/bigquery_slot_usage_time` limit but no
`bigquery_slot_usage_time` usage row.

Do not apply that zero-usage inference to every missing dimension. Per-user
read-request usage may be unavailable even when project-level read-request
usage exists, so display it as a limit-only row unless Monitoring provides a
matching per-user series.

To deliberately create a tiny usage sample for the BigQuery raster-function
slot-time quota, use the explicit probe helper:

```powershell
python scripts/probe_bigquery_slot_usage.py --project PROJECT_ID
python scripts/probe_bigquery_slot_usage.py --project PROJECT_ID --run --ack-cost --refresh-quota
```

The default command only prints the SQL. The `--run --ack-cost` form creates a
real BigQuery job using `ST_REGIONSTATS`, so run it only after the user accepts
possible quota/cost consumption. Cloud Monitoring can take a few minutes to
publish the new usage series.

## Required Local Access

For live quota values:

- Google Cloud CLI installed and initialized, preferably through
  `scripts/ensure_gcloud_cli.py --project PROJECT_ID --run`.
- The user is logged in with `gcloud auth login`.
- The project is selected or passed explicitly with `--project`.
- The caller has `cloudquotas.quotas.get` on the project.

For recent usage:

- The caller also needs `monitoring.timeSeries.list`.
- Cloud Monitoring must have quota usage time series for the selected window.

## Useful Commands

```powershell
python scripts/ensure_gcloud_cli.py --project PROJECT_ID
python scripts/ensure_gcloud_cli.py --project PROJECT_ID --run
gcloud auth login
gcloud config set project PROJECT_ID
gcloud beta quotas info list --service=earthengine.googleapis.com --project=PROJECT_ID --format=json
python scripts/show_ee_quotas.py --project PROJECT_ID
python scripts/show_ee_quotas.py --project PROJECT_ID --include-usage
```

If `gcloud beta quotas info list` is missing, install the beta component or let
the helper fall back to the Cloud Quotas REST API:

```powershell
gcloud components install beta
```

## Earth Engine Default Reference

Official Earth Engine quota docs list these defaults or fixed limits:

- Max concurrent requests, standard endpoint: 40 concurrent requests per
  project.
- Max concurrent requests, high-volume endpoint: 40 concurrent requests per
  project.
- Max request rate: 100 requests/s or 6000 requests/min per project.
- Max request rate: 100 requests/s or 6000 requests/min per account.
- Average concurrent batch tasks: 2 tasks on average, with tier/payment-plan
  details for some projects.
- Max asset storage: 250 GB.
- Max asset count: 10,000 assets.
- Daily EECU-time limit: unlimited by default unless a project quota is set.
- BigQuery raster function slot-time: 1,260,000 slot-seconds/day
  (350 slot-hours).
- READY task queue length: 3,000 tasks.
- Request payload size: 10 MB.
- Large aggregation result size: 100 MiB.

## Noncommercial Tier Interpretation

Earth Engine noncommercial projects have three current tiers:

- Community Tier: 150 EECU-hours per month, or 540,000 EECU-seconds.
- Contributor Tier: 1,000 EECU-hours per month, or 3,600,000 EECU-seconds.
- Partner Tier: 100,000 EECU-hours per month, or 360,000,000 EECU-seconds.

The `EECU-time per day` quota is a daily guardrail/cost-control limit and is
unlimited by default. It is separate from the recurring monthly noncommercial
EECU quota. A project can therefore show `EECU-seconds per day: Unlimited`
while also having a finite monthly noncommercial quota such as
`Noncommercial EECU-seconds per month: 540,000`.

The public Earth Engine `ProjectConfig` REST resource exposes registration
state, such as commercial or non-commercial registration, but not a documented
tier-name field. EasyGEE therefore infers the noncommercial tier from the live
monthly EECU system limit when available and labels the UI value as inferred.

## Interpretation Notes

- A quota table is a limit/guardrail, not proof that a specific analysis will
  succeed. Earth Engine code can still fail from memory, aggregation, payload,
  projection, or timeout limits.
- "Unlimited" in Console means no explicit quota value is configured for that
  limit, not unlimited compute in every technical sense.
- Do not suggest bypassing quotas with multiple accounts. Earth Engine
  explicitly treats quota circumvention as a Terms of Service violation.

## Scripts

- Use `scripts/show_ee_quotas.py --project <project>` or pass a Cloud Console
  quota URL when the user asks for quota values. Use `--include-usage` only
  when the user asks for recent/current usage. Report whether results are live
  Cloud Quotas/Monitoring data or official fallback defaults.
- Use `scripts/refresh_map_console_quota.py <map.html>` after UI-only edits to
  an existing Map Console HTML file when quota state needs to be refreshed.
  This updates only `STATE.quota` and refuses to write default-only fallback
  quota state unless `--allow-fallback` is explicitly provided.
- Use `scripts/probe_bigquery_slot_usage.py --project <project>` when the
  BigQuery raster function slot-time quota shows a live limit but no usage
  time series. Explain that no Monitoring series usually means zero recent
  usage for that quota, not missing authorization, if other Earth Engine usage
  metrics are present. The probe prints a tiny `ST_REGIONSTATS` BigQuery SQL
  sample by default; run it only with `--run --ack-cost` after the user
  explicitly accepts that it creates a BigQuery job and can consume quota/cost.

## Operating Rules

- For quota display, parse the project id from the Console URL when present,
  run `show_ee_quotas.py`, and never print `gcloud auth print-access-token`
  output, OAuth URLs, service account keys, or credential file contents.
- For normal Map Console pages, leave live quota lookup enabled so the UI can
  show Cloud Quotas / Monitoring status. Use `--no-live-quota` only for offline
  tests, smoke runs, or explicitly requested no-network previews; for non-sample
  pages the generator requires the explicit `--allow-default-quota-state` guard
  before it will write default-only quota state.
- For UI-only Map Console maintenance, do not regenerate a user-facing page
  with `--no-live-quota` or `--no-quota-usage`. Patch the source/generated HTML
  for the UI change, then run `refresh_map_console_quota.py` if the page's
  embedded quota state needs refreshing. If live quota lookup is unavailable,
  leave the existing page state unchanged and explain the quota lookup failure
  instead of downgrading the UI to default-only quota status.
