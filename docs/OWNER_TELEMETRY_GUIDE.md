## Owner Telemetry & Integrity Checks

This feature is **optional** and intended for the package owner to:

- Detect when `callflow-tracer` is used in a new environment.
- Receive an email containing a basic integrity report (checksums) and environment info.
- Detect potential tampering of critical package files.

It is **not** a security boundary: users who control the environment can disable
network access, remove this code, or change it.

### 1. Generating integrity checksums

Before building or publishing a new version, regenerate `checksums.json`:

```bash
cd path/to/callflow-tracer
python scripts/generate_checksums.py
```

This writes `callflow_tracer/checksums.json` with SHA-256 hashes for all
important `.py` files in the package. The build script (`build.py`) already
runs this step automatically before building.

### 2. Email notification configuration (SendGrid)

Email notifications are sent via the SendGrid v3 API. To enable reporting:

1. Create a SendGrid account and an API key with permission to send mail.
2. Set the following environment variables in the environment where you build
   or run your code:

   - `CALLFLOW_TRACER_SENDGRID_API_KEY` – your SendGrid API key
   - `CALLFLOW_TRACER_OWNER_EMAIL` – the email address that should receive notifications
   - `CALLFLOW_TRACER_FROM_EMAIL` – the from-address used when sending mail

3. (Recommended) Install `requests`:

```bash
pip install requests
```

Without `requests`, the reporting functions will simply report `sent=False`.

### 3. Triggering usage reporting

There are two ways to trigger reporting:

#### a) Explicit call in your code

```python
from callflow_tracer import init_owner_reporting, report_usage

# One-time initialization (respects CALLFLOW_TRACER_AUTOREPORT)
init_owner_reporting(username="your-github-or-owner-name")

# Or explicitly force a report (ignores AUTOREPORT flag)
report_usage(username="your-github-or-owner-name")
```

#### b) Auto-report via environment variable

Set:

- `CALLFLOW_TRACER_AUTOREPORT=1`

Then call `init_owner_reporting()` once during program startup. When enabled,
this will:

1. Compute an installation ID and basic environment info.
2. Verify integrity using `callflow_tracer.integrity_check.verify_integrity()`.
3. Send a structured JSON payload in the email body to `CALLFLOW_TRACER_OWNER_EMAIL`.

### 4. What information is sent

The email body contains a JSON document with:

- Timestamp and a stable `installation_id` for the machine.
- Optional `username` (you pass it in).
- Package metadata: name and version.
- Basic environment info (Python version, OS/platform, machine type, hostname).
- Integrity report: expected vs actual SHA-256 for each tracked file, and a
  flag indicating whether all hashes match.

### 5. Limitations & privacy notes

- Anyone with access to the code or environment can:
  - Comment out or remove telemetry functions.
  - Override environment variables.
  - Block or proxy outbound HTTP requests.
  - Fork/modify the repository and remove checksum checks.
- Because this repository is public, **you cannot prevent copying** of the
  source code. You can only **detect usage in environments where the telemetry
  is left intact and network access is available**.
- Be transparent with your users about any telemetry you enable and what data
  is sent. Consider making telemetry opt-in in your own applications.


