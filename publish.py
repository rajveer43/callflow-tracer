#!/usr/bin/env python3
"""
Publish script for callflow-tracer.

Supported targets:
- testpypi
- pypi
- both

Examples:
    python publish.py testpypi --yes
    python publish.py pypi --yes
    python publish.py both --yes
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and handle errors."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        print(f"❌ {description} failed")
        if exc.stdout:
            print("STDOUT:")
            print(exc.stdout)
        if exc.stderr:
            print("STDERR:")
            print(exc.stderr)
        return False

    print(f"✅ {description} completed successfully")
    if result.stdout.strip():
        print(result.stdout.strip())
    return True


def check_environment() -> bool:
    """Check if the environment is ready for publishing."""
    print("🔍 Checking environment...")

    if not os.path.exists("pyproject.toml"):
        print(
            "❌ Error: pyproject.toml not found. Please run this script from the package root directory."
        )
        return False

    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Error: dist/ directory not found. Building will create it.")
        return True

    dist_files = list(dist_dir.glob("*"))
    if dist_files:
        print(f"✅ Found {len(dist_files)} distribution files")
        for file in dist_files:
            print(f"   - {file.name}")
    else:
        print("⚠️  dist/ exists but is empty. A build will be required.")

    return True


def build_package() -> bool:
    """Build the package before publishing."""
    print("🏗️  Building package...")
    return run_command(
        [sys.executable, "build.py", "--skip-check"],
        "Building package for distribution",
    )


def check_dist_ready() -> bool:
    """Ensure the dist directory has built artifacts."""
    dist_files = list(Path("dist").glob("*"))
    if not dist_files:
        print("❌ Error: No distribution files found in dist/. Run the build first.")
        return False
    return True


def upload(target: str) -> bool:
    """Upload artifacts to the selected repository."""
    if target == "testpypi":
        print("🧪 Uploading to Test PyPI...")
        cmd = [sys.executable, "-m", "twine", "upload", "--repository", "testpypi"]
        description = "Uploading to Test PyPI"
    else:
        print("📦 Uploading to PyPI...")
        cmd = [sys.executable, "-m", "twine", "upload"]
        description = "Uploading to PyPI"

    cmd.append("dist/*")

    if not run_command(cmd, description):
        return False

    if target == "testpypi":
        print("\n🔗 Test PyPI URL: https://test.pypi.org/project/callflow-tracer/")
        print("Install from Test PyPI:")
        print("pip install --index-url https://test.pypi.org/simple/ callflow-tracer")
    else:
        print("\n🔗 PyPI URL: https://pypi.org/project/callflow-tracer/")
        print("Install from PyPI:")
        print("pip install callflow-tracer")

    return True


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Publish callflow-tracer to PyPI")
    parser.add_argument(
        "target",
        nargs="?",
        choices=["testpypi", "pypi", "both"],
        help="Publish target",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation prompts",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Do not build before publishing",
    )
    return parser.parse_args(argv)


def confirm(targets: List[str]) -> bool:
    """Ask for confirmation before publishing."""
    print("\n⚠️  WARNING: This will upload the package to:")
    for target in targets:
        print(f" - {target}")
    print("Make sure you have:")
    print("1. Updated the version number")
    print("2. Tested the package locally")
    print("3. Configured twine credentials in ~/.pypirc")

    choice = input("\nDo you want to continue? (y/N): ").strip().lower()
    return choice in {"y", "yes"}


def main(argv: Optional[List[str]] = None) -> int:
    """Main publish process."""
    args = parse_args(argv or sys.argv[1:])

    print("🚀 CallFlow Tracer - Publish Script")
    print("=" * 50)

    if not check_environment():
        return 1

    if args.target is None:
        print("\nChoose upload target:")
        print("1. Test PyPI")
        print("2. PyPI")
        print("3. Both")
        selection = input("Enter choice (1, 2, or 3): ").strip()
        target_map = {"1": "testpypi", "2": "pypi", "3": "both"}
        target = target_map.get(selection)
        if not target:
            print("❌ Invalid choice.")
            return 1
    else:
        target = args.target

    targets = ["testpypi", "pypi"] if target == "both" else [target]

    if not args.yes and not confirm(targets):
        print("❌ Upload cancelled.")
        return 0

    if not args.skip_build:
        if not build_package():
            return 1
    elif not check_dist_ready():
        return 1

    if not check_dist_ready():
        return 1

    for upload_target in targets:
        if not upload(upload_target):
            print(f"❌ Upload to {upload_target} failed!")
            return 1

    print("\n🎉 Publishing completed successfully!")
    print("\nNext steps:")
    print("1. Verify the package on the target index")
    print("2. Push the release tag to git")
    print("3. Announce the release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
