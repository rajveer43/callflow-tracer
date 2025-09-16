#!/usr/bin/env python3
"""
Build script for callflow-tracer package.
This script builds the package for distribution.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
import argparse
import importlib.util
import time

def run_command(cmd, description, timeout=300):
    """Run a command and handle errors with timeout."""
    print(f"[BUILD] {description}...")
    start_time = time.time()
    
    try:
        # Use timeout to prevent hanging
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        print(f"[OK] {description} completed successfully ({elapsed:.1f}s)")
        
        if result.stdout and result.stdout.strip():
            print("Output:", result.stdout.strip()[:500])  # Limit output
        return True
        
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {description} timed out after {timeout}s")
        return False
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"[FAIL] {description} failed after {elapsed:.1f}s: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout.strip()[:500])
        if e.stderr:
            print("STDERR:", e.stderr.strip()[:500])
        return False

def clean_build():
    """Clean previous build artifacts."""
    print("[CLEAN] Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'callflow_tracer.egg-info', '.egg-info']
    files_to_clean = ['MANIFEST.in']
    
    # Clean directories
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"   Removed {dir_name}/")
            except PermissionError:
                print(f"   Warning: Could not remove {dir_name}/ (permission denied)")
    
    # Clean files
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"   Removed {file_name}")
            except PermissionError:
                print(f"   Warning: Could not remove {file_name} (permission denied)")
    
    # Clean __pycache__ directories
    pycache_count = 0
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # Use slice to allow modification during iteration
            if dir_name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, dir_name))
                    pycache_count += 1
                    dirs.remove(dir_name)  # Don't recurse into removed directory
                except PermissionError:
                    pass
    
    if pycache_count > 0:
        print(f"   Removed {pycache_count} __pycache__ directories")

def check_requirements():
    """Check if required files exist."""
    required_files = ['pyproject.toml']
    missing_files = []
    
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing_files.append(file_name)
    
    if missing_files:
        print(f"[ERROR] Missing required files: {', '.join(missing_files)}")
        print("[ERROR] Please run this script from the package root directory.")
        return False
    
    return True

def ensure_tools_installed(skip_deps: bool) -> bool:
    """Ensure build tools are available without reinstalling every run."""
    if skip_deps:
        print("[INFO] Skipping dependency check")
        return True

    def is_installed(module_name: str) -> bool:
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError, AttributeError):
            return False

    # Check required tools with their actual module names
    tools_to_check = {
        "build": "build",
        "twine": "twine"
    }
    
    missing_tools = []
    for tool_name, module_name in tools_to_check.items():
        if not is_installed(module_name):
            missing_tools.append(tool_name)
            print(f"[INFO] {tool_name} not found")
        else:
            print(f"[INFO] {tool_name} is available")

    if not missing_tools:
        print("[INFO] All build tools are installed")
        return True

    print(f"[INFO] Installing missing tools: {', '.join(missing_tools)}")
    
    # Install missing tools with timeout
    install_cmd = f"pip install --upgrade {' '.join(missing_tools)}"
    return run_command(install_cmd, "Installing missing build tools", timeout=180)

def build_package(skip_deps: bool, skip_clean: bool) -> bool:
    """Build the package."""
    print("[BUILD] Building callflow-tracer package...")

    # Check requirements
    if not check_requirements():
        return False

    # Ensure tools are installed only if missing
    if not ensure_tools_installed(skip_deps):
        return False

    # Clean previous builds (optional)
    if not skip_clean:
        clean_build()
    else:
        print("[INFO] Skipped cleaning (using existing dist if any)")

    # First check if build module is available
    try:
        import build
        build_available = True
    except ImportError:
        build_available = False
        print("[WARNING] 'build' module not available, trying setuptools...")
    
    print("[INFO] Starting package build (this may take a few minutes)...")
    
    # Try different build methods
    if build_available:
        # Method 1: python -m build with no isolation
        build_cmd = "python -m build --no-isolation"
        if run_command(build_cmd, "Building package (no isolation)", timeout=300):
            pass  # Success, continue
        else:
            print("[INFO] Trying with isolation...")
            # Method 2: python -m build with isolation
            fallback_cmd = "python -m build"
            if not run_command(fallback_cmd, "Building package (with isolation)", timeout=600):
                print("[INFO] Trying setuptools fallback...")
                # Method 3: Direct setuptools fallback
                if not run_command("python setup.py sdist bdist_wheel", "Building with setuptools", timeout=300):
                    return False
    else:
        # Direct setuptools method
        if not run_command("python setup.py sdist bdist_wheel", "Building with setuptools", timeout=300):
            return False

    print("[OK] Package built successfully!")
    
    # List build artifacts
    dist_dir = Path("dist")
    if dist_dir.exists() and list(dist_dir.iterdir()):
        print("\n[INFO] Build artifacts:")
        total_size = 0
        for file in dist_dir.iterdir():
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                total_size += size_kb
                print(f"   - {file.name} ({size_kb:.1f} KB)")
        print(f"   Total: {total_size:.1f} KB")
    else:
        print("[WARNING] No build artifacts found in dist/")
        return False

    return True

def check_package(skip_check: bool):
    """Check the built package."""
    if skip_check:
        print("[INFO] Skipped twine check")
        return True

    print("[CHECK] Checking package...")

    # Check if dist directory has files
    dist_dir = Path("dist")
    if not dist_dir.exists() or not list(dist_dir.glob("*")):
        print("[ERROR] No files found in dist/ directory")
        return False

    # Check with twine
    if not run_command("twine check dist/*", "Checking package with twine", timeout=120):
        print("[WARNING] Twine check failed, but build artifacts exist")
        print("[INFO] You may still be able to install/upload the package")
        return True  # Don't fail the entire build for twine check issues

    print("[OK] Package check passed!")
    return True

def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description="Build callflow-tracer package")
    parser.add_argument("--skip-deps", action="store_true", 
                       help="Skip installing/checking build dependencies")
    parser.add_argument("--skip-clean", action="store_true", 
                       help="Skip cleaning build artifacts before building")
    parser.add_argument("--skip-check", action="store_true", 
                       help="Skip twine validation check")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()

    print("CallFlow Tracer - Build Script")
    print("=" * 50)
    
    # Show current directory and Python version
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version.split()[0]}")
    
    start_time = time.time()

    try:
        # Build the package
        if not build_package(skip_deps=args.skip_deps, skip_clean=args.skip_clean):
            print("[FAIL] Build failed!")
            sys.exit(1)

        # Check the package
        if not check_package(skip_check=args.skip_check):
            print("[FAIL] Package check failed!")
            sys.exit(1)

        total_time = time.time() - start_time
        print(f"\n[OK] Build completed successfully in {total_time:.1f}s!")
        
        print("\nNext steps:")
        print("1. Test locally: pip install dist/callflow_tracer-*.whl")
        print("2. Upload to PyPI: python publish.py")
        print("3. Or upload manually: twine upload dist/*")
        
    except KeyboardInterrupt:
        print("\n[INFO] Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()