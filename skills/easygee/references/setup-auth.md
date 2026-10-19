# Setup And Auth

Use this reference when installing GEE/geemap, checking a local environment,
authenticating, initializing a Cloud project, or debugging auth errors.

## Official Sources

- geemap installation: https://geemap.org/installation/
- Earth Engine auth/init: https://developers.google.com/earth-engine/guides/auth
- Earth Engine Python install: https://developers.google.com/earth-engine/guides/python_install

The core facts verified on 2026-07-04:

- `geemap` requires an approved Earth Engine account.
- Supported install paths include `uv pip install geemap`, `pip install geemap`,
  and `conda install geemap -c conda-forge`.
- Local Python workflows authenticate with `ee.Authenticate()` and initialize
  with `ee.Initialize(project='my-project')`.
- Existing credentials may be reused. Do not inspect or print credential files.
- Earth Engine authentication supports environment-specific modes such as
  `localhost`, `notebook`, `gcloud`, and `colab`.
- `earthengine set_project PROJECT_ID` configures a default project, but
  reusable code should still prefer explicit `ee.Initialize(project=...)`.

## Environment Choice

Prefer the current project environment if it already declares Python tooling.
Otherwise:

- Lightweight scripts: use `uv` or the user's current Python.
- Heavy GIS stack on Windows: prefer a fresh conda/mamba environment when
  available, because optional geospatial dependencies can be brittle.
- Keep reusable envs in a dedicated environments directory, not inside a
  project repo, and point EasyGEE at the interpreter with `EASYGEE_PYTHON` or
  settings.json `pythonPath`.

Example commands:

```powershell
# Lightweight uv install into an active environment
uv pip install geemap

# Plain pip install into the active Python
python -m pip install geemap

# Conda/mamba path when available
conda create -n gee python=3.13
conda activate gee
conda install geemap -c conda-forge
```

## Standard Authentication Flow

Use `scripts/ee_auth_workflow.py` before giving auth instructions. It prints a
credential-safe, user-run workflow and does not open OAuth, read credentials, or
print tokens.

```powershell
python scripts/ee_auth_workflow.py --project YOUR_EE_PROJECT --mode localhost
python scripts/ee_auth_workflow.py --project YOUR_EE_PROJECT --mode notebook --include-auth-snippet
python scripts/ee_auth_workflow.py --project YOUR_EE_PROJECT --mode gcloud
```

## Standard geemap Authorization Flow

Use `scripts/geemap_auth_workflow.py` when the user specifically says
"geemap auth", "geemap authorization", "geemap login", or asks how geemap
authenticates.

```powershell
python scripts/geemap_auth_workflow.py --project YOUR_EE_PROJECT --mode localhost
python scripts/geemap_auth_workflow.py --project YOUR_EE_PROJECT --mode notebook --include-auth-snippet
```

The important distinction: geemap does not maintain a separate Google login or
credential file. geemap uses the `earthengine-api` Python package. The user
authorizes Earth Engine once with OAuth, then every geemap notebook/script
initializes Earth Engine explicitly:

```python
import ee
import geemap

ee.Initialize(project="my-earthengine-project")
m = geemap.Map()
```

Before OAuth is complete, `geemap` can still be imported and may render local
basemap-only maps, but Earth Engine datasets, EE tiles, server-side reducers,
and exports require successful `ee.Initialize(project=...)`.

## One-Sentence geemap + Quota Authorization

Use `scripts/authorize_geemap_once.py` when the user wants authorization to be
as simple as one sentence, for example:

> 帮我授权 geemap 到 example-ee-project-123456

The agent may then run a single guarded flow in the intended Python
environment:

```powershell
python scripts/authorize_geemap_once.py --project YOUR_EE_PROJECT --run --quota-mode required
```

What this can automate:

1. Check that `earthengine-api`, `geemap`, and the `earthengine` CLI are
   available in the selected Python environment.
2. If credentials are missing, launch
   `earthengine authenticate --auth_mode=localhost` for browser OAuth.
3. Suppress OAuth command output so auth URLs, verification codes, and tokens
   are not copied into chat or logs.
4. Run `earthengine set_project YOUR_EE_PROJECT`.

Project selection is user-local state. EasyGEE should remember a successfully
verified project in its local user settings and also respect the user's
Earth Engine/gcloud defaults on later runs. Do not commit a real user's project
id into repository files; use placeholders in docs and tests.
5. Verify `ee.Initialize(project="YOUR_EE_PROJECT")` with
   `scripts/check_gee_geemap.py`.
6. Ensure Google Cloud CLI is available as the fixed EasyGEE resource at
   `%LOCALAPPDATA%\EasyGEE\tools\google-cloud-sdk` (Windows default; override
   with `EASYGEE_GCLOUD_ROOT`) when it is missing.
7. Check Google Cloud CLI authentication without printing account tokens.
8. Set the same Cloud project in `gcloud`.
9. Probe Cloud Quotas and Cloud Monitoring so the browser UI can show quota
   total/used/remaining when permissions and metrics are available.

What cannot be automated:

- Google OAuth consent must still be approved by the user in the browser.
- Google Cloud CLI can be installed as EasyGEE's fixed resource from the
  official Google archive, but network/firewall problems can still block the
  download.
- The user must have an approved Earth Engine account and access to the Cloud
  project.
- The Earth Engine API must be enabled and the project must be registered for
  the relevant commercial or noncommercial Earth Engine use.
- The Google account must have Cloud Quotas access such as
  `cloudquotas.quotas.get`; current usage/remaining also needs Cloud Monitoring
  access such as `monitoring.timeSeries.list`.

Before actually launching OAuth, show the dry plan:

```powershell
python scripts/authorize_geemap_once.py --project YOUR_EE_PROJECT
```

Use `--skip-auth` only when credentials are already present and the agent only
needs to set the project and verify. Use `--force-auth` only when the user
explicitly wants to refresh OAuth.

Quota options:

- `--quota-mode auto`: try quota setup and report soft blockers.
- `--quota-mode required`: fail the flow if live Cloud quota totals are
  unavailable.
- `--quota-mode required-usage`: also fail if Cloud Monitoring usage rows are
  unavailable, which means remaining quota cannot be computed.
- `--quota-mode skip`: skip Cloud quota checks.

## Fixed Google Cloud CLI Resource

Use `scripts/ensure_gcloud_cli.py` when setup specifically concerns the Google
Cloud CLI:

```powershell
python scripts/ensure_gcloud_cli.py --project YOUR_EE_PROJECT
python scripts/ensure_gcloud_cli.py --project YOUR_EE_PROJECT --run
```

The standard fixed Windows location is
`%LOCALAPPDATA%\EasyGEE\tools\google-cloud-sdk` (`~/.local/share/easygee/google-cloud-sdk`
elsewhere). Use the
bundled-Python Google Cloud CLI archive there so direct `gcloud.cmd` calls do
not depend on the shell's PATH. This keeps the CLI out of project repos and
makes quota tooling reusable across EasyGEE tasks. The detector also honors
`EASYGEE_GCLOUD` for an exact CLI path and `EASYGEE_GCLOUD_ROOT` for a custom
fixed SDK directory.

`--run` may download and extract Google's official Windows archive, open
`gcloud auth login`, run `gcloud config set project YOUR_EE_PROJECT`, and probe
Earth Engine Cloud Quotas/Monitoring access. OAuth output is suppressed; never
ask the user to paste auth URLs, codes, tokens, credential files, or
`gcloud auth print-access-token` output into chat.

## User Onboarding Inputs

The only value the agent normally needs from the user is the Earth Engine /
Google Cloud **Project ID**, for example `my-gee-project-123456`.

Ask the user to get it from official Google pages:

1. Sign in or register Earth Engine access:
   https://earthengine.google.com/signup/
2. Review Earth Engine access/registration requirements:
   https://developers.google.com/earth-engine/guides/access
3. Open Google Cloud Console and create or choose a project:
   https://console.cloud.google.com/
4. Copy the **Project ID** from the project selector or project dashboard. Do
   not confuse it with project name or project number.
5. Enable the Earth Engine API for that project:
   https://console.cloud.google.com/apis/library/earthengine.googleapis.com
6. Confirm Earth Engine commercial/noncommercial project configuration:
   https://console.cloud.google.com/earth-engine/configuration

Never ask the user to send OAuth tokens, verification codes, credential files,
service account JSON, API keys, browser authorization URLs, or the contents of
`~/.config/earthengine/credentials`.

Agent sequence:

1. Run `scripts/check_gee_geemap.py` with the target Python to see packages,
   Earth Engine CLI, credential-file presence, and optional initialization.
2. Ask for or discover the intended Earth Engine / Google Cloud project id.
3. For one-sentence geemap auth requests, run
   `scripts/authorize_geemap_once.py --project PROJECT` first. Use
   `--run --quota-mode required` only after the user explicitly asks to proceed.
4. For explanatory geemap-specific auth requests, run
   `scripts/geemap_auth_workflow.py --project PROJECT --mode auto`; otherwise
   run `scripts/ee_auth_workflow.py --project PROJECT --mode auto`. Give the
   user the printed setup steps.
5. Let the user complete OAuth in their browser or notebook. Do not paste or
   request auth URLs, verification codes, tokens, or credential files.
6. Verify only after the user says auth is complete, or after
   `authorize_geemap_once.py --run` finishes:

```powershell
python scripts/check_gee_geemap.py --project YOUR_EE_PROJECT --initialize
```

Local Windows example with an explicit shared environment (replace
`<ENV>` with the environment directory, `<PLUGIN>` with the EasyGEE plugin root):

```powershell
& '<ENV>/Scripts/python.exe' '<PLUGIN>/skills/easygee/scripts/ee_auth_workflow.py' --project YOUR_EE_PROJECT --mode localhost
& '<ENV>/Scripts/earthengine.exe' authenticate --auth_mode=localhost
& '<ENV>/Scripts/earthengine.exe' set_project YOUR_EE_PROJECT
& '<ENV>/Scripts/python.exe' '<PLUGIN>/skills/easygee/scripts/check_gee_geemap.py' --project YOUR_EE_PROJECT --initialize
```

Notebook setup cell:

Use an authentication cell only during setup or interactive notebooks:

```python
import ee

ee.Authenticate()  # or ee.Authenticate(auth_mode="notebook")
ee.Initialize(project="my-earthengine-project")
```

Reusable script cell:

```python
import ee

PROJECT = "my-earthengine-project"
ee.Initialize(project=PROJECT)
```

CLI equivalents:

```powershell
earthengine authenticate --auth_mode=localhost
earthengine set_project my-earthengine-project
earthengine --project my-earthengine-project ls
```

Do not run authentication automatically in scripts that should be reusable or
headless. Put auth in a setup cell, setup command, or user-guided step.

## Mode Selection

- **Local workstation**: prefer `localhost` when a browser runs on the same
  machine.
- **Notebook/Jupyter**: use `notebook` when a notebook auth page/code flow is
  more reliable than a terminal browser flow.
- **Colab**: use `colab`.
- **gcloud-managed environments**: use `gcloud` when the Google Cloud SDK is
  installed and Application Default Credentials/quota project are expected.
- **Service account**: reserve for unattended apps, REST, VMs, or CI-style
  workflows. A normal interactive Python/geemap user account does not require a
  service account.

## Credential Safety

Never commit or reveal:

- `~/.config/earthengine/credentials`
- service account JSON keys
- OAuth tokens
- Google Cloud API keys
- copied browser auth URLs containing secrets

When checking readiness, report only whether credential paths exist, not their
contents.

## Common Failures

- **No Cloud project**: ask for the Earth Engine / Google Cloud project id and
  use `ee.Initialize(project='...')`.
- **API not enabled / 403**: the selected Cloud project may not have Earth
  Engine API enabled or the user may lack permission.
- **Quota or usage questions**: use `scripts/show_ee_quotas.py --project
  YOUR_EE_PROJECT` or read `quota-monitoring.md`. Quota display should report
  whether values came from live Cloud Quotas/Monitoring data or official
  Earth Engine defaults.
- **No approved EE account**: geemap can install, but Earth Engine requests will
  fail until the account/application is approved.
- **Remote shell auth problems**: choose an auth mode suited to the runtime
  (`localhost`, `notebook`, `gcloud`, or `colab`) and avoid assuming a browser
  is available.
- **Service account workflows**: do not add service account keys to a repo.
  Prefer environment-managed secrets and pass credentials explicitly at runtime.

## Environment Check First

- Check the environment before installing or authenticating:
   - Run `python scripts/check_gee_geemap.py` from this skill directory, or read
     the script and run it with an explicit Python executable.
   - Use `--project <cloud-project-id> --initialize` only when the user has
     provided the project id or it is discoverable from the current repo config.

## Scripts

- Use `scripts/check_gee_geemap.py` for a quick local readiness report.
- Use `scripts/easygee_project.py resolve --json` when an EasyGEE workflow
  needs the user's Earth Engine / Google Cloud project id and none was passed
  explicitly. It resolves from user-level local settings, environment,
  Earth Engine defaults, and gcloud config without reading credential file
  contents or writing the id into the repository.
- Use `scripts/ensure_gcloud_cli.py --project <project>` when Google Cloud CLI
  status, installation, login, project selection, or quota readiness is part of
  the setup. The fixed resource location defaults to
  `%LOCALAPPDATA%\EasyGEE\tools\google-cloud-sdk` on Windows
  (`~/.local/share/easygee/google-cloud-sdk` elsewhere), with `EASYGEE_GCLOUD`
  (exact CLI path) / `EASYGEE_GCLOUD_ROOT` (SDK directory) as explicit
  overrides. Use `--run` only when the user asks for one-command setup; it may
  install the official Google archive, open browser login, set the project, and
  probe live quotas without printing OAuth URLs, codes, tokens, or credential
  contents.
- Use `scripts/ee_auth_workflow.py --project <project> --mode auto` when the
  user asks to authenticate, initialize Earth Engine, fix project/quota auth
  errors, or standardize setup. Give the user the printed commands; do not run
  OAuth automatically or request tokens/verification codes in chat.
- Use `scripts/geemap_auth_workflow.py --project <project> --mode auto` when
  the user says "geemap auth", "geemap authorization", "geemap login", or asks
  how geemap completes authorization. Explain that geemap reuses
  `earthengine-api` OAuth credentials and has no separate credential store.
- Use `scripts/authorize_geemap_once.py --project <project>` when the user asks
  whether authorization can be reduced to one sentence, or wants a preview of
  the one-sentence flow. Use `--run` only when the user explicitly asks to
  proceed, for example "帮我授权 geemap 到 example-ee-project-123456". This runner
  can launch browser OAuth, set the Earth Engine project, verify
  `ee.Initialize(project=...)`, then check Google Cloud Quotas/Monitoring access
  for quota total/used/remaining without reading or printing credential
  contents. Use `--quota-mode required` for the standard one-sentence flow so
  missing `gcloud` is resolved through the fixed EasyGEE Google Cloud CLI
  resource when possible, and Cloud Quotas or Monitoring access is caught during
  auth rather than later in the browser UI.

## Operating Rules

- Prefer `ee.Initialize(project='...')` over project-less initialization. Earth
  Engine now expects an explicit Cloud project in most local Python workflows.
- Treat the Earth Engine project id as user-level local configuration, not
  repository state. Do not hard-code a user's project id into docs, code, test
  fixtures, generated HTML committed to git, or plugin bundles. After a
  successful authorization, persist it only through EasyGEE local settings or
  the user's Earth Engine/gcloud environment, and reuse it on later plugin
  runs.
- For authentication, follow the standard ladder in `references/setup-auth.md`:
  diagnose with `check_gee_geemap.py`, generate user-run steps with
  `ee_auth_workflow.py`, let the user complete OAuth, then verify with
  `check_gee_geemap.py --initialize`.
- For geemap authorization specifically, use `geemap_auth_workflow.py` as the
  user-facing entrypoint while keeping the same credential-safety rules. Do not
  imply geemap has a separate login system.
- For one-sentence geemap authorization requests, run
  `authorize_geemap_once.py --project PROJECT` first to show the safe plan. If
  the user has clearly asked to start the authorization, run it with
  `--run --quota-mode required` in the intended Python environment, let the
  user approve Google OAuth / Google Cloud CLI login in the browser when
  prompted, then report the final verification status for both geemap and quota
  access. Never ask the user to paste OAuth codes, auth URLs, tokens, service
  account keys, or credential file contents into chat.
- On Windows, prefer a fresh shared environment for heavy geospatial stacks
  when possible. Keep reusable Python environments in a dedicated environments
  directory outside project repos, and point EasyGEE at it with
  `EASYGEE_PYTHON` or settings.json `pythonPath`.
