#!/usr/bin/env python3
"""
Version management script for callflow-tracer.
This script helps manage version numbers and updates all relevant files.
"""

import re
import sys
from pathlib import Path

def get_current_version():
    """Get the current version from pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        return match.group(1)
    return None

def update_version(new_version):
    """Update version in all relevant files."""
    print(f"📝 Updating version to {new_version}...")
    
    # Update pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    
    with open("pyproject.toml", "w") as f:
        f.write(content)
    
    print("✅ Updated pyproject.toml")
    
    # Update __init__.py
    init_file = Path("callflow_tracer/__init__.py")
    if init_file.exists():
        with open(init_file, "r") as f:
            content = f.read()
        
        content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
        
        with open(init_file, "w") as f:
            f.write(content)
        
        print("✅ Updated callflow_tracer/__init__.py")
    
    print(f"✅ Version updated to {new_version}")

def validate_version(version):
    """Validate version format."""
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        print(f"❌ Invalid version format: {version}")
        print("Version should be in format: X.Y.Z (e.g., 1.0.0)")
        return False
    return True

def main():
    """Main version management process."""
    print("🔢 CallFlow Tracer - Version Manager")
    print("=" * 50)
    
    current_version = get_current_version()
    if current_version:
        print(f"Current version: {current_version}")
    else:
        print("❌ Could not determine current version")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("\nUsage: python version.py <new_version>")
        print("Example: python version.py 1.0.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    if not validate_version(new_version):
        sys.exit(1)
    
    if new_version == current_version:
        print(f"⚠️  Version {new_version} is already the current version")
        sys.exit(0)
    
    print(f"\nUpdating from {current_version} to {new_version}")
    update_version(new_version)
    
    print(f"\n🎉 Version updated successfully!")
    print("\nNext steps:")
    print("1. Test the package: python test_example.py")
    print("2. Build the package: python build.py")
    print("3. Publish the package: python publish.py")

if __name__ == "__main__":
    main()
