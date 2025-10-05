# Installation and Setup Guide

Complete guide for installing and setting up CallFlow Tracer.

---

## 📋 Table of Contents

1. [Requirements](#requirements)
2. [Installation Methods](#installation-methods)
3. [Verification](#verification)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Upgrading](#upgrading)

---

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: 512MB minimum (2GB recommended for large traces)
- **Disk Space**: 50MB for package, additional space for trace data

### Python Dependencies
- **Required**:
  - No required dependencies! (works out of the box)
  
- **Optional** (for enhanced features):
  - `networkx` - For graph operations
  - `numpy` - For numerical operations in examples
  - `jupyter` - For Jupyter notebook integration
  - `ipython` - For magic commands

### Browser Requirements (for HTML visualizations)
- Modern web browser with JavaScript enabled
- Internet connection (for CDN resources) or offline mode
- Recommended: Chrome, Firefox, Safari, Edge

---

## Installation Methods

### Method 1: PyPI (Recommended)

Install the latest stable version from PyPI:

```bash
pip install callflow-tracer
```

With optional dependencies:

```bash
# For Jupyter support
pip install callflow-tracer jupyter ipython

# For all optional features
pip install callflow-tracer[all]
```

### Method 2: From Source

Clone and install from GitHub:

```bash
# Clone repository
git clone https://github.com/rajveer43/callflow-tracer.git
cd callflow-tracer

# Install in development mode
pip install -e .

# Or install with optional dependencies
pip install -e ".[dev]"
```

### Method 3: Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/rajveer43/callflow-tracer.git
cd callflow-tracer

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Method 4: Virtual Environment (Recommended)

Using venv:

```bash
# Create virtual environment
python -m venv callflow-env

# Activate (Windows)
callflow-env\Scripts\activate

# Activate (Unix/macOS)
source callflow-env/bin/activate

# Install package
pip install callflow-tracer
```

Using conda:

```bash
# Create conda environment
conda create -n callflow python=3.8

# Activate environment
conda activate callflow

# Install package
pip install callflow-tracer
```

---

## Verification

### Quick Test

Verify installation with a simple test:

```python
# test_installation.py
from callflow_tracer import trace_scope

def test_function():
    return "Hello, CallFlow Tracer!"

with trace_scope() as graph:
    result = test_function()
    print(result)

print(f"✓ Installation successful!")
print(f"  Traced {len(graph.nodes)} nodes")
print(f"  Found {len(graph.edges)} edges")
```

Run the test:

```bash
python test_installation.py
```

Expected output:
```
Hello, CallFlow Tracer!
✓ Installation successful!
  Traced 1 nodes
  Found 0 edges
```

### Check Version

```python
import callflow_tracer
print(callflow_tracer.__version__)
```

### Run Test Suite

```bash
# Run all tests
cd tests
python test_flamegraph.py
python test_jupyter_integration.py
python test_cprofile_fix.py
```

### Run Examples

```bash
# Run flamegraph examples
cd examples
python flamegraph_example.py

# Run enhanced demo
python flamegraph_enhanced_demo.py
```

---

## Configuration

### Default Configuration

CallFlow Tracer works out of the box with sensible defaults. No configuration required!

### Environment Variables

Optional environment variables:

```bash
# Set default output directory
export CALLFLOW_OUTPUT_DIR="./traces"

# Set default color scheme
export CALLFLOW_COLOR_SCHEME="performance"

# Enable debug mode
export CALLFLOW_DEBUG=1
```

### Configuration File (Optional)

Create `callflow.config.json` in your project root:

```json
{
  "output_dir": "./traces",
  "default_layout": "hierarchical",
  "color_scheme": "performance",
  "show_stats": true,
  "search_enabled": true,
  "flamegraph": {
    "width": 1600,
    "height": 1000,
    "min_width": 0.1
  },
  "profiling": {
    "enable_cpu": true,
    "enable_memory": true,
    "enable_io": true
  }
}
```

Load configuration:

```python
import json
from callflow_tracer import trace_scope, export_html

# Load config
with open('callflow.config.json') as f:
    config = json.load(f)

# Use config
with trace_scope() as graph:
    my_function()

export_html(
    graph,
    f"{config['output_dir']}/trace.html",
    layout=config['default_layout']
)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Import Error

**Error**:
```
ImportError: No module named 'callflow_tracer'
```

**Solutions**:
1. Verify installation: `pip list | grep callflow`
2. Check Python version: `python --version` (must be 3.8+)
3. Ensure correct environment is activated
4. Reinstall: `pip install --force-reinstall callflow-tracer`

#### Issue 2: Permission Error

**Error**:
```
PermissionError: [Errno 13] Permission denied
```

**Solutions**:
1. Use user installation: `pip install --user callflow-tracer`
2. Use virtual environment (recommended)
3. Run with sudo (not recommended): `sudo pip install callflow-tracer`

#### Issue 3: Version Conflict

**Error**:
```
ERROR: Cannot install callflow-tracer due to conflicting dependencies
```

**Solutions**:
1. Create fresh virtual environment
2. Update pip: `pip install --upgrade pip`
3. Install with `--no-deps` flag: `pip install --no-deps callflow-tracer`

#### Issue 4: HTML Not Opening

**Error**: Generated HTML file doesn't open or shows errors

**Solutions**:
1. Check internet connection (for CDN resources)
2. Try different browser
3. Check browser console for JavaScript errors
4. Verify file was created: `ls -la output.html`

#### Issue 5: Jupyter Integration Not Working

**Error**: Magic commands not recognized

**Solutions**:
1. Install Jupyter: `pip install jupyter ipython`
2. Initialize integration: `from callflow_tracer.jupyter import init_jupyter; init_jupyter()`
3. Restart Jupyter kernel
4. Check IPython version: `ipython --version`

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from callflow_tracer import trace_scope

with trace_scope() as graph:
    my_function()
```

### Getting Help

If you encounter issues:

1. Check documentation: `docs/` directory
2. Search GitHub issues: https://github.com/rajveer43/callflow-tracer/issues
3. Create new issue with:
   - Python version
   - Package version
   - Operating system
   - Full error traceback
   - Minimal reproduction code

---

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade callflow-tracer
```

### Upgrade from Specific Version

```bash
# Check current version
pip show callflow-tracer

# Upgrade to latest
pip install --upgrade callflow-tracer

# Or specify version
pip install callflow-tracer==0.3.0
```

### Migration Guide

#### From 0.2.2 to Latest

**No breaking changes!** All existing code works.

New features are opt-in:

```python
# Old code (still works)
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    my_function()

generate_flamegraph(graph, "output.html")

# New features (optional)
generate_flamegraph(
    graph,
    "output.html",
    color_scheme="performance",  # NEW!
    show_stats=True,             # NEW!
    search_enabled=True          # NEW!
)
```

#### Deprecated Features

None currently. All features are maintained.

---

## Platform-Specific Notes

### Windows

```bash
# Use PowerShell or Command Prompt
pip install callflow-tracer

# Activate virtual environment
.\venv\Scripts\activate

# Run examples
python examples\flamegraph_example.py
```

### macOS

```bash
# Install with Homebrew Python (recommended)
brew install python@3.9
pip3 install callflow-tracer

# Or use system Python
python3 -m pip install callflow-tracer
```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get install python3-pip
pip3 install callflow-tracer

# Fedora/RHEL
sudo dnf install python3-pip
pip3 install callflow-tracer

# Arch Linux
sudo pacman -S python-pip
pip install callflow-tracer
```

---

## Docker Installation

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install callflow-tracer
RUN pip install callflow-tracer

# Copy your code
COPY . /app
WORKDIR /app

# Run your traced application
CMD ["python", "your_app.py"]
```

Build and run:

```bash
docker build -t my-traced-app .
docker run -v $(pwd)/traces:/app/traces my-traced-app
```

---

## IDE Integration

### VS Code

Install Python extension and add to `settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.analysis.extraPaths": [
    "./venv/lib/python3.9/site-packages"
  ]
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click "+" to add package
3. Search for "callflow-tracer"
4. Click "Install Package"

### Jupyter Lab

```bash
# Install Jupyter Lab
pip install jupyterlab

# Install callflow-tracer
pip install callflow-tracer

# Start Jupyter Lab
jupyter lab
```

---

## Uninstallation

```bash
# Uninstall package
pip uninstall callflow-tracer

# Remove configuration (optional)
rm -rf ~/.callflow

# Remove virtual environment (if used)
rm -rf callflow-env
```

---

## Next Steps

After installation:

1. **Quick Start**: See [README.md](../README.md)
2. **Examples**: Run examples in `examples/` directory
3. **Documentation**: Read `docs/` directory
4. **API Reference**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
5. **Features**: Check [FEATURES_COMPLETE.md](FEATURES_COMPLETE.md)

---

## Support

- 📧 Email: rathodrajveer1311@gmail.com
- 🐛 Issues: https://github.com/rajveer43/callflow-tracer/issues
- 📖 Docs: https://github.com/rajveer43/callflow-tracer/wiki
- 💬 Discussions: https://github.com/rajveer43/callflow-tracer/discussions

---

*Installation Guide - Last Updated: 2025-10-05*
