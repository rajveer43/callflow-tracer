#!/usr/bin/env python3
"""
Publish script for callflow-tracer package.
This script uploads the package to PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def check_environment():
    """Check if the environment is ready for publishing."""
    print("🔍 Checking environment...")
    
    # Check if dist directory exists
    if not os.path.exists("dist"):
        print("❌ Error: dist/ directory not found. Please run build.py first.")
        return False
    
    # Check if there are any distribution files
    dist_files = list(Path("dist").glob("*"))
    if not dist_files:
        print("❌ Error: No distribution files found in dist/ directory.")
        return False
    
    print(f"✅ Found {len(dist_files)} distribution files")
    for file in dist_files:
        print(f"   - {file.name}")
    
    return True

def upload_to_test_pypi():
    """Upload to Test PyPI first."""
    print("🧪 Uploading to Test PyPI...")
    
    if not run_command("twine upload --repository testpypi dist/*", "Uploading to Test PyPI"):
        return False
    
    print("✅ Uploaded to Test PyPI successfully!")
    print("\n🔗 Test PyPI URL: https://test.pypi.org/project/callflow-tracer/")
    print("\nTo test the package from Test PyPI:")
    print("pip install --index-url https://test.pypi.org/simple/ callflow-tracer")
    
    return True

def upload_to_pypi():
    """Upload to PyPI."""
    print("📦 Uploading to PyPI...")
    
    if not run_command("twine upload dist/*", "Uploading to PyPI"):
        return False
    
    print("✅ Uploaded to PyPI successfully!")
    print("\n🔗 PyPI URL: https://pypi.org/project/callflow-tracer/")
    print("\nTo install the package:")
    print("pip install callflow-tracer")
    
    return True

def main():
    """Main publish process."""
    print("🚀 CallFlow Tracer - Publish Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: pyproject.toml not found. Please run this script from the package root directory.")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Ask user for confirmation
    print("\n⚠️  WARNING: This will upload the package to PyPI!")
    print("Make sure you have:")
    print("1. Built the package with build.py")
    print("2. Tested the package locally")
    print("3. Updated the version number if needed")
    print("4. Created a PyPI account and configured twine")
    
    choice = input("\nDo you want to continue? (y/N): ").strip().lower()
    if choice not in ['y', 'yes']:
        print("❌ Upload cancelled.")
        sys.exit(0)
    
    # Ask for upload target
    print("\nChoose upload target:")
    print("1. Test PyPI (recommended for first upload)")
    print("2. PyPI (production)")
    
    target = input("Enter choice (1 or 2): ").strip()
    
    if target == "1":
        if not upload_to_test_pypi():
            print("❌ Upload to Test PyPI failed!")
            sys.exit(1)
    elif target == "2":
        if not upload_to_pypi():
            print("❌ Upload to PyPI failed!")
            sys.exit(1)
    else:
        print("❌ Invalid choice. Please run the script again.")
        sys.exit(1)
    
    print("\n🎉 Publishing completed successfully!")
    print("\nNext steps:")
    print("1. Verify the package on PyPI")
    print("2. Update your GitHub repository")
    print("3. Create a release tag")
    print("4. Announce the package!")

if __name__ == "__main__":
    main()
