# Installation Guide - CallFlow Tracer VS Code Extension

## Prerequisites

### 1. Python Requirements
- **Python 3.7+** installed and accessible
- **pip** package manager

### 2. Install CallFlow Tracer Python Package

```bash
# Install from PyPI (when published)
pip install callflow-tracer

# OR install from source (current development)
cd /path/to/callflow-tracer
pip install -e .
```

Verify installation:
```bash
python3 -c "import callflow_tracer; print(callflow_tracer.__version__)"
```

### 3. VS Code Requirements
- **Visual Studio Code** 1.75.0 or higher
- **Node.js** 16.x or higher (for development)

## Installation Methods

### Method 1: From VS Code Marketplace (Future)

Once published:

1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions)
3. Search for "CallFlow Tracer"
4. Click **Install**
5. Reload VS Code

### Method 2: Install from VSIX File

1. **Package the extension** (see Development Guide)
2. Open VS Code
3. Press `Ctrl+Shift+X` (Extensions)
4. Click `...` menu → **Install from VSIX...**
5. Select the `.vsix` file
6. Reload VS Code (`Ctrl+Shift+P` → "Reload Window")

### Method 3: Run from Source (Development)

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed instructions.

## Post-Installation Setup

### 1. Configure Python Path

If Python is not in your system PATH:

**Via Settings UI:**
1. Press `Ctrl+,` (Settings)
2. Search for "callflow"
3. Set **Python Path** to your Python executable

**Via settings.json:**
```json
{
  "callflowTracer.pythonPath": "/usr/bin/python3"
}
```

**Common paths:**
- Linux: `/usr/bin/python3`
- macOS: `/usr/local/bin/python3`
- Windows: `C:\\Python39\\python.exe`
- Virtual env: `/path/to/venv/bin/python`

### 2. Configure Default Settings

```json
{
  "callflowTracer.pythonPath": "python3",
  "callflowTracer.defaultLayout": "force",
  "callflowTracer.defaultSpacing": "normal",
  "callflowTracer.autoTrace": false,
  "callflowTracer.includeArgs": false,
  "callflowTracer.enableProfiling": true
}
```

## Verification

### Test the Extension

1. **Create a test file** `test_callflow.py`:

```python
from callflow_tracer import trace

@trace
def add(a, b):
    return a + b

@trace
def multiply(a, b):
    return a * b

@trace
def calculate():
    x = add(5, 3)
    y = multiply(x, 2)
    return y

@trace
def main():
    result = calculate()
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
```

2. **Open in VS Code**
3. **Right-click** in editor
4. Select **"CallFlow: Trace Current File"**
5. **Visualization should appear** in side panel

### Check Extension Status

1. Press `Ctrl+Shift+X` (Extensions)
2. Search for "CallFlow Tracer"
3. Should show **"Installed"** or **"Enabled"**

### Check Output Logs

1. Press `Ctrl+Shift+U` (Output panel)
2. Select **"CallFlow Tracer"** from dropdown
3. Check for any errors or warnings

## Troubleshooting

### Extension Not Found

**Problem:** Extension doesn't appear in Extensions panel

**Solutions:**
- Ensure `.vsix` file was installed correctly
- Reload VS Code: `Ctrl+Shift+P` → "Reload Window"
- Check VS Code version (must be 1.75.0+)

### Python Module Not Found

**Problem:** Error: `No module named 'callflow_tracer'`

**Solutions:**
```bash
# Verify Python installation
python3 -c "import callflow_tracer"

# Reinstall package
pip install --upgrade callflow-tracer

# Check pip list
pip list | grep callflow

# If using virtual env, activate it first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Trace Command Fails

**Problem:** Trace runs but no output

**Solutions:**
1. Check Output panel for errors
2. Verify Python file has `if __name__ == "__main__"` block
3. Ensure functions are decorated with `@trace`
4. Try a simpler test file first

### Visualization Not Loading

**Problem:** Panel opens but blank

**Solutions:**
1. Open DevTools: `Help` → `Toggle Developer Tools`
2. Check Console for JavaScript errors
3. Verify internet connection (for vis.js CDN)
4. Try clearing trace: `CallFlow: Clear Trace Data`

### Permission Errors

**Problem:** Cannot write trace files

**Solutions:**
```bash
# Check file permissions
ls -la /path/to/your/file.py

# Ensure write access to directory
chmod +w /path/to/directory
```

## Uninstallation

### Remove Extension

1. Press `Ctrl+Shift+X` (Extensions)
2. Find "CallFlow Tracer"
3. Click **Uninstall**
4. Reload VS Code

### Remove Python Package

```bash
pip uninstall callflow-tracer
```

### Clean Settings

Remove from `settings.json`:
```json
{
  "callflowTracer.pythonPath": "...",
  "callflowTracer.defaultLayout": "...",
  // Remove all callflowTracer.* settings
}
```

## Next Steps

- Read [README.md](README.md) for features overview
- See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
- Check [TESTING.md](TESTING.md) for testing instructions
- Visit [User Guide](docs/USER_GUIDE.md) for detailed usage

## Support

- **Issues:** https://github.com/rajveer/callflow-tracer/issues
- **Discussions:** https://github.com/rajveer/callflow-tracer/discussions
- **Email:** rathodrajveer1311@gmail.com

---

**Installation complete! Start tracing your Python code! 🚀**
