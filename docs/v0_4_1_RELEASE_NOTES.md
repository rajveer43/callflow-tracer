# CallFlow Tracer v0.4.1 Release Notes

Release focused on production packaging, module-level refactoring, and release automation.

---

## What Changed

### 1. Module-wise repository restructuring

The package now follows a clearer production layout with domain-specific modules:

- `callflow_tracer/core/`
- `callflow_tracer/visualization/`
- `callflow_tracer/performance/`
- `callflow_tracer/analysis/`
- `callflow_tracer/observability/`
- `callflow_tracer/command_line/`
- `callflow_tracer/funnel/`

Root modules remain as compatibility shims, so existing imports continue to work while new code can use the cleaner module paths.

### 2. Cleaner public API

The top-level package was reduced to a thinner facade. Library users are encouraged to import from the new domain modules directly:

- `callflow_tracer.core`
- `callflow_tracer.visualization`
- `callflow_tracer.performance`
- `callflow_tracer.analysis`
- `callflow_tracer.observability`
- `callflow_tracer.command_line`

### 3. Automated versioning

Version updates are now driven by `version.py`, which can infer semantic version bumps from git history and conventional commit patterns.

Supported flows:

- `python version.py auto`
- `python version.py patch`
- `python version.py minor`
- `python version.py major`

### 4. Automated publishing workflow

The publishing script now supports explicit targets:

- `python publish.py testpypi --yes`
- `python publish.py pypi --yes`
- `python publish.py both --yes`

This makes release uploads repeatable and avoids manual interactive selection.

### 5. Build and packaging fixes

The build pipeline was tightened to use the active Python interpreter and to avoid module-name collisions with the local `build.py` script.

This makes local builds and release packaging more reliable inside a virtual environment.

### 6. Formatting and documentation cleanup

The codebase was formatted with Black, and the README, publishing docs, examples, and module guides were updated to reflect the new structure and release flow.

---

## Compatibility

No breaking changes are expected for existing users because the old root-level modules still act as compatibility shims.

New code should prefer the domain-specific package paths for clarity and long-term maintenance.

---

## Recommended Upgrade Path

1. Pull the latest `main`
2. Update your imports to the new module paths where practical
3. Use `python version.py auto` for the next release
4. Build with `python build.py`
5. Publish with `python publish.py testpypi --yes` or `python publish.py pypi --yes`

---

## Release Checks

Validated for this release:

- Package build succeeds
- `twine check` succeeds
- CLI import path remains functional
- Version tag `v0.4.1` matches the package version

