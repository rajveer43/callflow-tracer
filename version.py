#!/usr/bin/env python3
"""
Version management script for callflow-tracer.

This script supports both manual version bumps and automatic semver bumps
based on conventional commit messages.

Automatic bump rules:
- `BREAKING CHANGE` or `!:` in the commit subject -> major
- `feat:` commits -> minor
- `fix:`, `perf:`, or non-breaking maintenance commits -> patch

Examples:
    python version.py auto
    python version.py auto --since v0.4.0
    python version.py minor
    python version.py 0.5.0
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
VERSION_FILE = Path("callflow_tracer/__init__.py")
PYPROJECT_FILE = Path("pyproject.toml")


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    content = PYPROJECT_FILE.read_text(encoding="utf-8")
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise RuntimeError("Unable to find version in pyproject.toml")
    return match.group(1)


def validate_version(version: str) -> bool:
    """Validate version format."""
    return bool(SEMVER_RE.match(version))


def bump_version(version: str, part: str) -> str:
    """Return a bumped semantic version."""
    match = SEMVER_RE.match(version)
    if not match:
        raise ValueError(f"Invalid semantic version: {version}")

    major, minor, patch = map(int, match.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unsupported bump part: {part}")


def update_version(new_version: str) -> None:
    """Update version in all relevant files."""
    print(f"Updating version to {new_version}...")

    pyproject_content = PYPROJECT_FILE.read_text(encoding="utf-8")
    pyproject_content = re.sub(
        r'version = "[^"]+"', f'version = "{new_version}"', pyproject_content
    )
    PYPROJECT_FILE.write_text(pyproject_content, encoding="utf-8")
    print("Updated pyproject.toml")

    if VERSION_FILE.exists():
        init_content = VERSION_FILE.read_text(encoding="utf-8")
        init_content = re.sub(
            r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', init_content
        )
        VERSION_FILE.write_text(init_content, encoding="utf-8")
        print("Updated callflow_tracer/__init__.py")


def _run_git(args: List[str]) -> str:
    """Run a git command and return stdout, or raise a clear error."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_latest_git_tag() -> Optional[str]:
    """Return the latest semver-ish git tag, if any."""
    try:
        tags = _run_git(["tag", "--sort=-v:refname"]).splitlines()
    except Exception:
        return None

    for tag in tags:
        cleaned = tag.lstrip("v")
        if validate_version(cleaned):
            return tag
    return None


def get_commits_since(ref: Optional[str]) -> List[str]:
    """Collect commit subjects and bodies since a reference."""
    git_args = ["log", "--format=%s%n%b"]
    if ref:
        git_args.insert(2, f"{ref}..HEAD")

    try:
        output = _run_git(git_args)
    except Exception:
        return []

    commits = [block.strip() for block in output.split("\n\n") if block.strip()]
    return commits


def infer_bump_level(commits: Iterable[str]) -> Tuple[str, str]:
    """
    Infer semver bump level from conventional commit messages.

    Returns:
        (level, reason)
    """
    has_breaking = False
    has_feature = False
    has_fix_or_perf = False
    has_changes = False

    for commit in commits:
        if not commit:
            continue
        has_changes = True
        lines = [line.strip() for line in commit.splitlines() if line.strip()]
        subject = lines[0] if lines else ""
        body = "\n".join(lines[1:])
        lowered = subject.lower()

        if "breaking change" in body.lower() or re.match(
            r"^[a-z]+(?:\([^)]+\))?!:", lowered
        ):
            has_breaking = True
            break
        if lowered.startswith("feat"):
            has_feature = True
        if lowered.startswith("fix") or lowered.startswith("perf"):
            has_fix_or_perf = True

    if has_breaking:
        return "major", "breaking change detected"
    if has_feature:
        return "minor", "feature commit detected"
    if has_fix_or_perf:
        return "patch", "fix/performance commit detected"
    if has_changes:
        return "patch", "defaulting to patch for non-feature changes"
    return "patch", "no commits found; defaulting to patch"


def auto_bump_version(since: Optional[str] = None) -> Tuple[str, str, str]:
    """Compute the next version automatically from git history."""
    current = get_current_version()
    ref = since or get_latest_git_tag() or f"v{current}"
    commits = get_commits_since(ref)
    level, reason = infer_bump_level(commits)
    new_version = bump_version(current, level)
    return new_version, level, reason


def parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="CallFlow Tracer version manager")
    parser.add_argument(
        "version",
        help="Target version, bump level (major/minor/patch), or 'auto'",
    )
    parser.add_argument(
        "--since",
        help="Git reference to analyze for auto bumping (default: latest version tag)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the computed version without writing files",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Main version management process."""
    args = parse_args(argv or sys.argv[1:])
    current_version = get_current_version()
    target = args.version.strip().lower()

    if target == "auto":
        new_version, level, reason = auto_bump_version(args.since)
        print(f"Current version: {current_version}")
        print(f"Auto bump level: {level} ({reason})")
        print(f"Next version: {new_version}")
        if args.dry_run:
            return 0
        if new_version == current_version:
            print("Version is already up to date")
            return 0
        update_version(new_version)
        print("Version updated successfully")
        return 0

    if target in {"major", "minor", "patch"}:
        new_version = bump_version(current_version, target)
        print(f"Current version: {current_version}")
        print(f"Requested bump: {target}")
        print(f"Next version: {new_version}")
        if args.dry_run:
            return 0
        update_version(new_version)
        print("Version updated successfully")
        return 0

    new_version = args.version
    if not validate_version(new_version):
        print("Version should be in format X.Y.Z (for example 1.0.0)")
        return 1

    print(f"Current version: {current_version}")
    print(f"Target version: {new_version}")
    if args.dry_run:
        return 0
    if new_version == current_version:
        print("Version is already the current version")
        return 0

    update_version(new_version)
    print("Version updated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
