# 🚀 Quick Install & Test - 5 Minutes

## Step 1: Install the Extension (1 min)

```bash
# Open VS Code
code
```

**In VS Code**:
1. Click **Extensions** icon (left sidebar, or `Ctrl+Shift+X`)
2. Click **...** menu (three dots at the top)
3. Select **"Install from VSIX..."**
4. Paste this path:
   ```
   /Users/rajveerrathod/Work/personal_projects/callflow-tracer/vscode-extension/callflow-tracer-2.1.0.vsix
   ```
5. Click **Install**
6. **Result**: See "CallFlow Tracer" in extensions list ✓

---

## Step 2: Create a Test File (1 min)

**File**: Create `test_trace.py` anywhere

```python
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    """Main function."""
    result = fibonacci(10)
    print(f"Fib(10) = {result}")

if __name__ == "__main__":
    main()
```

---

## Step 3: Trace the File (2 min)

1. **Open** `test_trace.py` in VS Code
2. **Command Palette**: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. **Type**: `CallFlow: Trace Current File`
4. **Press Enter**
5. **Wait** for analysis to complete

---

## Step 4: View Results (1 min)

**You should see**:
- ✓ Visualization panel opens
- ✓ Graph showing function dependencies
- ✓ `fibonacci` calls itself
- ✓ `main` calls `fibonacci`

**Check Output Panel**:
- `Ctrl+Shift+U` to open Output
- Select "CallFlow Tracer" dropdown
- See analysis logs:
  ```
  ✓ Starting trace...
  ✓ Analyzing dependencies...
  ✓ Found circular dependencies
  ✓ Trace complete
  ```

---

## Troubleshooting (If Not Working)

### Python Not Found

```bash
# Check where Python is
which python3

# Set in VS Code Settings:
# Ctrl+, to open Settings
# Search: callflowTracer.pythonPath
# Set to: /usr/local/bin/python3 (or your path)
```

### Extension Not Installing

```bash
# Install from command line instead
code --install-extension \
  /Users/rajveerrathod/Work/personal_projects/callflow-tracer/vscode-extension/callflow-tracer-2.1.0.vsix
```

### Commands Not Showing

```bash
# Reload VS Code
Cmd+Shift+P → Type "Reload Window" → Enter
```

---

## Test These Commands Next

Try these in Command Palette (`Ctrl+Shift+P`):

```
CallFlow: Show Visualization       ← View the trace graph
CallFlow: Export as JSON           ← Save trace to JSON
CallFlow: Clear Trace Data         ← Clear for new trace
CallFlow: Generate Summary         ← Get trace analysis summary
```

---

## Verify Refactored Code Is Working

**In VS Code Output Panel** (`Ctrl+Shift+U`):

Look for these lines (from refactored modules):

```
✓ Extracted nodes       ← From dependency_analyzer.py
✓ Analyzing dependencies
✓ Found circular deps
✓ Tight coupling analysis
```

If you see these → **Refactored code is working! ✅**

---

## Success! 🎉

When you see:
- Extension installed ✓
- Visualization appears ✓  
- Output shows analysis logs ✓
- Commands work ✓

**Your extension is ready to use with the refactored Python modules!**

---

## Next: Advanced Testing

See `LOCAL_TESTING_GUIDE.md` for:
- Advanced test cases
- Performance testing
- All commands reference
- Troubleshooting details

---

**Time**: ~5 minutes  
**Status**: ✅ Ready to test
