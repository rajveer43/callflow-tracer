# Testing Guide - CallFlow Tracer VS Code Extension

## Quick Start - Test Locally

### Step 1: Setup

```bash
# Navigate to extension directory
cd /path/to/callflow-tracer/vscode-extension

# Install dependencies
npm install

# Ensure Python package is installed
pip install -e ../
```

### Step 2: Open in VS Code

```bash
code .
```

### Step 3: Launch Extension Development Host

**Press F5** or:
1. Go to **Run and Debug** panel (Ctrl+Shift+D)
2. Select **"Run Extension"** from dropdown
3. Click **green play button** or press F5

This opens a new VS Code window titled **"[Extension Development Host]"**

### Step 4: Create Test File

In the Extension Development Host window:

1. **Create new file:** `test_trace.py`
2. **Add test code:**

```python
from callflow_tracer import trace
import time

@trace
def slow_function():
    time.sleep(0.1)
    return "slow"

@trace
def fast_function():
    time.sleep(0.01)
    return "fast"

@trace
def process_data():
    result1 = fast_function()
    result2 = slow_function()
    return f"{result1} and {result2}"

@trace
def main():
    result = process_data()
    print(result)

if __name__ == "__main__":
    main()
```

3. **Save the file** (Ctrl+S)

### Step 5: Test Tracing

**Method 1: Context Menu**
1. Right-click in the editor
2. Select **"CallFlow: Trace Current File"**
3. Wait for progress notification
4. Visualization panel should open

**Method 2: Command Palette**
1. Press `Ctrl+Shift+P`
2. Type "CallFlow: Trace Current File"
3. Press Enter

**Method 3: Editor Title Icon**
1. Look for graph icon in editor title bar
2. Click it to trace

### Step 6: Verify Visualization

The visualization panel should show:
- ✅ 4 nodes (slow_function, fast_function, process_data, main)
- ✅ Edges connecting the functions
- ✅ Color coding (red for slow, blue for fast)
- ✅ Stats at top (4 functions, relationships, duration)

### Step 7: Test Controls

**Test Layout Switching:**
1. Click **Layout** dropdown
2. Try each layout:
   - Hierarchical
   - Force-Directed
   - Circular
   - Radial Tree
   - Grid
   - Tree (Vertical)
   - Tree (Horizontal)
   - Timeline
   - Organic

**Test Spacing:**
1. Click **Spacing** dropdown
2. Try: Compact → Normal → Relaxed → Wide
3. Observe nodes spreading out

**Test Physics:**
1. Select "Force-Directed" layout
2. Toggle **Physics**: Enabled → Disabled
3. Nodes should stop/start moving

### Step 8: Test Export

**Export JSON:**
1. Click **"Export JSON"** button
2. Choose save location
3. Verify JSON file created

**Export PNG:**
1. Click **"Export PNG"** button
2. Check for success message

### Step 9: Check Debug Output

**In original VS Code window:**
1. View **Debug Console** (Ctrl+Shift+Y)
2. Check for extension logs
3. Look for any errors

**In Extension Development Host:**
1. Open **Output** panel (Ctrl+Shift+U)
2. Select **"CallFlow Tracer"** from dropdown
3. Check Python execution logs

## Comprehensive Test Suite

### Test 1: Basic Tracing

**Test File:** `test_basic.py`
```python
from callflow_tracer import trace

@trace
def add(a, b):
    return a + b

@trace
def main():
    result = add(5, 3)
    print(result)

if __name__ == "__main__":
    main()
```

**Expected:**
- ✅ 2 nodes (add, main)
- ✅ 1 edge (main → add)
- ✅ No errors

### Test 2: Nested Calls

**Test File:** `test_nested.py`
```python
from callflow_tracer import trace

@trace
def level3():
    return "level3"

@trace
def level2():
    return level3()

@trace
def level1():
    return level2()

@trace
def main():
    result = level1()
    print(result)

if __name__ == "__main__":
    main()
```

**Expected:**
- ✅ 4 nodes
- ✅ 3 edges (main → level1 → level2 → level3)
- ✅ Hierarchical layout shows clear depth

### Test 3: Multiple Calls

**Test File:** `test_multiple.py`
```python
from callflow_tracer import trace

@trace
def helper():
    return "help"

@trace
def main():
    # Call helper multiple times
    for i in range(5):
        helper()

if __name__ == "__main__":
    main()
```

**Expected:**
- ✅ 2 nodes
- ✅ Edge shows "5 calls"
- ✅ Edge is thicker (width scales with calls)

### Test 4: Complex Graph

**Test File:** `test_complex.py`
```python
from callflow_tracer import trace

@trace
def db_query():
    return "data"

@trace
def cache_check():
    return None

@trace
def fetch_data():
    cached = cache_check()
    if not cached:
        return db_query()
    return cached

@trace
def process():
    data = fetch_data()
    return data.upper()

@trace
def validate():
    return True

@trace
def main():
    if validate():
        result = process()
        print(result)

if __name__ == "__main__":
    main()
```

**Expected:**
- ✅ 6 nodes
- ✅ Multiple edges
- ✅ Force-directed layout shows natural clustering

### Test 5: Error Handling

**Test File:** `test_error.py`
```python
from callflow_tracer import trace

@trace
def will_fail():
    raise ValueError("Test error")

@trace
def main():
    try:
        will_fail()
    except ValueError:
        print("Caught error")

if __name__ == "__main__":
    main()
```

**Expected:**
- ✅ Trace completes despite error
- ✅ Functions still appear in graph
- ✅ Error logged in Output panel

### Test 6: Trace Selection

1. Open `test_complex.py`
2. Select the `process()` function (highlight the def line)
3. Right-click → **"CallFlow: Trace Selected Function"**

**Expected:**
- ✅ Only traces `process()` and its callees
- ✅ Smaller graph focused on that function

### Test 7: Auto-Trace on Save

1. Enable in settings:
   ```json
   {
     "callflowTracer.autoTrace": true
   }
   ```
2. Open `test_basic.py`
3. Make a change (add a comment)
4. Save file (Ctrl+S)

**Expected:**
- ✅ Trace runs automatically
- ✅ Visualization updates

### Test 8: Different Python Paths

**Test with virtual environment:**
```bash
# Create venv
python3 -m venv test_venv
source test_venv/bin/activate
pip install -e /path/to/callflow-tracer
```

**Configure:**
```json
{
  "callflowTracer.pythonPath": "/path/to/test_venv/bin/python"
}
```

**Expected:**
- ✅ Uses venv Python
- ✅ Trace works correctly

### Test 9: Large Graph

**Test File:** `test_large.py`
```python
from callflow_tracer import trace

# Create 20 functions
@trace
def func_1(): return func_2()
@trace
def func_2(): return func_3()
# ... continue to func_20

@trace
def main():
    func_1()

if __name__ == "__main__":
    main()
```

**Expected:**
- ✅ All 20 nodes appear
- ✅ Grid layout works well
- ✅ Compact spacing helps
- ✅ No performance issues

### Test 10: Clear Trace

1. Run any trace
2. Press `Ctrl+Shift+P`
3. Run **"CallFlow: Clear Trace Data"**

**Expected:**
- ✅ Visualization panel closes
- ✅ Success message appears
- ✅ Next trace starts fresh

## Testing Checklist

### Core Features
- [ ] Trace current file
- [ ] Trace selected function
- [ ] Show visualization
- [ ] Clear trace data
- [ ] Export JSON
- [ ] Export PNG

### Layouts
- [ ] Hierarchical
- [ ] Force-Directed
- [ ] Circular
- [ ] Radial Tree
- [ ] Grid
- [ ] Tree (Vertical)
- [ ] Tree (Horizontal)
- [ ] Timeline
- [ ] Organic

### Controls
- [ ] Layout switching works
- [ ] Spacing adjustment works
- [ ] Physics toggle works
- [ ] All controls update graph

### Settings
- [ ] Python path configuration
- [ ] Default layout setting
- [ ] Default spacing setting
- [ ] Auto-trace on save
- [ ] Include args setting
- [ ] Enable profiling setting

### UI Elements
- [ ] Context menu items appear
- [ ] Command palette commands work
- [ ] Editor title icon appears
- [ ] Activity bar icon appears
- [ ] Status bar item appears
- [ ] Webview panel loads

### Error Handling
- [ ] Invalid Python file
- [ ] Python not found
- [ ] Module import errors
- [ ] Syntax errors in Python
- [ ] Network errors (vis.js CDN)
- [ ] File permission errors

## Automated Testing

### Run Linter

```bash
npm run lint
```

**Expected:** No errors or warnings

### Fix Linting Issues

```bash
npm run lint -- --fix
```

### Unit Tests (Future)

Create `test/extension.test.js`:

```javascript
const assert = require('assert');
const vscode = require('vscode');

suite('Extension Test Suite', () => {
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('rajveer-rathod.callflow-tracer'));
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands();
        assert.ok(commands.includes('callflow-tracer.traceFile'));
        assert.ok(commands.includes('callflow-tracer.showVisualization'));
    });
});
```

Run tests:
```bash
npm test
```

## Performance Testing

### Test 1: Trace Speed

1. Create file with 50+ functions
2. Time the trace operation
3. Should complete in < 5 seconds

### Test 2: Visualization Rendering

1. Generate large graph (50+ nodes)
2. Open visualization
3. Should render in < 2 seconds

### Test 3: Layout Switching

1. Open large graph
2. Switch between layouts
3. Each switch should be < 1 second

### Test 4: Memory Usage

1. Open DevTools → Memory
2. Take heap snapshot
3. Run multiple traces
4. Take another snapshot
5. Check for memory leaks

## Debugging Tests

### Enable Verbose Logging

Add to `extension.js`:
```javascript
const DEBUG = true;

function log(...args) {
    if (DEBUG) {
        console.log('[CallFlow]', ...args);
    }
}
```

### Check Python Output

Add to trace script:
```python
import sys
print("Starting trace...", file=sys.stderr)
# ... trace code ...
print("Trace complete!", file=sys.stderr)
```

### Inspect Webview

1. Open visualization
2. Right-click in webview
3. Select **"Inspect"**
4. Check Console for errors

## Common Test Failures

### "No module named 'callflow_tracer'"

**Fix:**
```bash
pip install -e /path/to/callflow-tracer
python3 -c "import callflow_tracer"  # Verify
```

### "Network not initialized"

**Fix:**
- Check vis.js CDN is accessible
- Verify webview HTML is generated
- Check browser console for errors

### "Trace data not generated"

**Fix:**
- Verify Python file has `if __name__ == "__main__":`
- Check Python execution didn't error
- Look at Output panel for Python errors

### Visualization is blank

**Fix:**
- Check nodes and edges arrays are populated
- Verify vis.js loaded (check Network tab)
- Check for JavaScript errors in console

## Test Reports

### Manual Test Report Template

```markdown
## Test Report - [Date]

### Environment
- OS: [Linux/macOS/Windows]
- VS Code Version: [1.75.0]
- Python Version: [3.9.0]
- Extension Version: [1.0.0]

### Tests Executed
- [x] Basic tracing
- [x] Layout switching
- [x] Export functions
- [ ] Auto-trace (failed)

### Issues Found
1. Auto-trace causes lag on large files
   - Severity: Medium
   - Workaround: Disable auto-trace

### Recommendations
- Add debounce to auto-trace
- Optimize large graph rendering
```

## Continuous Testing

### Pre-Commit Checks

```bash
#!/bin/bash
# .git/hooks/pre-commit

npm run lint
if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix errors."
    exit 1
fi

echo "All checks passed!"
```

### CI/CD (Future)

GitHub Actions workflow:
```yaml
name: Test Extension

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      - run: npm install
      - run: npm run lint
      - run: npm test
```

## Getting Help

If tests fail:

1. **Check logs** - Debug Console and Output panel
2. **Simplify** - Test with minimal example
3. **Isolate** - Test each component separately
4. **Report** - Create issue with test case

**Support:**
- Issues: https://github.com/rajveer/callflow-tracer/issues
- Discussions: https://github.com/rajveer/callflow-tracer/discussions

---

**Happy testing! 🧪**
