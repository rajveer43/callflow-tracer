# Development Guide - CallFlow Tracer VS Code Extension

## Setup Development Environment

### Prerequisites

1. **Node.js & npm**
   ```bash
   # Check versions
   node --version  # Should be 16.x or higher
   npm --version   # Should be 8.x or higher
   ```

2. **VS Code**
   - Version 1.75.0 or higher
   - Recommended extensions:
     - ESLint
     - Prettier
     - JavaScript Debugger

3. **Python & CallFlow Tracer**
   ```bash
   # Install Python package from source
   cd /path/to/callflow-tracer
   pip install -e .
   ```

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rajveer/callflow-tracer.git
   cd callflow-tracer/vscode-extension
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Open in VS Code**
   ```bash
   code .
   ```

## Project Structure

```
vscode-extension/
├── extension.js           # Main extension code
├── package.json          # Extension manifest
├── README.md             # User documentation
├── INSTALLATION.md       # Installation guide
├── DEVELOPMENT.md        # This file
├── TESTING.md           # Testing guide
├── CHANGELOG.md         # Version history
├── LICENSE              # MIT license
├── .vscodeignore        # Files to exclude from package
├── .eslintrc.json       # ESLint configuration
├── images/              # Icons and screenshots
│   ├── icon.png
│   ├── activity-bar-icon.svg
│   └── screenshot.png
├── test/                # Test files
│   └── extension.test.js
└── docs/                # Additional documentation
    ├── USER_GUIDE.md
    └── API.md
```

## Running the Extension

### Method 1: Debug Mode (Recommended)

1. **Open the extension folder** in VS Code
   ```bash
   cd vscode-extension
   code .
   ```

2. **Press F5** or select **Run → Start Debugging**
   - This opens a new "Extension Development Host" window
   - The extension is loaded and active in this window

3. **Test the extension** in the Development Host:
   - Open a Python file
   - Right-click → "CallFlow: Trace Current File"
   - View visualization

4. **View debug output**:
   - Original window: Debug Console shows extension logs
   - Dev Host window: Output panel shows trace logs

### Method 2: Run Without Debugging

1. Press `Ctrl+F5` or select **Run → Run Without Debugging**
2. Same as debug mode but without breakpoint support

### Method 3: Package and Install

1. **Install vsce** (VS Code Extension Manager)
   ```bash
   npm install -g @vscode/vsce
   ```

2. **Package the extension**
   ```bash
   vsce package
   # Creates: callflow-tracer-1.0.0.vsix
   ```

3. **Install the VSIX**
   - In VS Code: Extensions → `...` → Install from VSIX
   - Or command line:
     ```bash
     code --install-extension callflow-tracer-1.0.0.vsix
     ```

## Development Workflow

### 1. Make Code Changes

Edit `extension.js` or other files:

```javascript
// Example: Add a new command
vscode.commands.registerCommand('callflow-tracer.myNewCommand', () => {
    vscode.window.showInformationMessage('My new command!');
});
```

### 2. Reload Extension

**In Extension Development Host:**
- Press `Ctrl+R` or `Cmd+R` (macOS)
- Or: `Ctrl+Shift+P` → "Reload Window"

**Changes take effect immediately!**

### 3. Debug with Breakpoints

1. **Set breakpoints** in `extension.js`
   - Click left of line number
   - Red dot appears

2. **Trigger the code** in Dev Host
   - Run a command that hits the breakpoint

3. **Debug controls**:
   - `F5` - Continue
   - `F10` - Step Over
   - `F11` - Step Into
   - `Shift+F11` - Step Out
   - `Shift+F5` - Stop

4. **Inspect variables**:
   - Hover over variables
   - Check Variables panel
   - Use Debug Console

### 4. View Logs

**Extension logs:**
```javascript
console.log('Debug message');
console.error('Error message');
```

View in:
- Debug Console (original window)
- Output panel → "CallFlow Tracer" (Dev Host)

**Python trace logs:**
- Output panel → "CallFlow Tracer"
- Check stderr/stdout from Python execution

## Common Development Tasks

### Add a New Command

1. **Register in `package.json`:**
   ```json
   {
     "contributes": {
       "commands": [
         {
           "command": "callflow-tracer.myCommand",
           "title": "CallFlow: My Command"
         }
       ]
     }
   }
   ```

2. **Implement in `extension.js`:**
   ```javascript
   context.subscriptions.push(
       vscode.commands.registerCommand('callflow-tracer.myCommand', myCommandHandler)
   );
   
   async function myCommandHandler() {
       vscode.window.showInformationMessage('Command executed!');
   }
   ```

3. **Test:**
   - Reload extension (`Ctrl+R` in Dev Host)
   - `Ctrl+Shift+P` → "CallFlow: My Command"

### Add a Configuration Setting

1. **Define in `package.json`:**
   ```json
   {
     "configuration": {
       "properties": {
         "callflowTracer.mySetting": {
           "type": "string",
           "default": "value",
           "description": "My new setting"
         }
       }
     }
   }
   ```

2. **Read in code:**
   ```javascript
   const config = vscode.workspace.getConfiguration('callflowTracer');
   const mySetting = config.get('mySetting', 'defaultValue');
   ```

### Modify Webview Content

1. **Edit `getWebviewContent()` function** in `extension.js`
2. **Update HTML/CSS/JavaScript**
3. **Reload extension**
4. **Re-open visualization panel**

### Update Graph Layouts

The layout logic is embedded in the webview HTML. To add a new layout:

1. **Add option to dropdown** in `getWebviewContent()`:
   ```html
   <option value="mynewlayout">My New Layout</option>
   ```

2. **Implement layout logic** in webview JavaScript:
   ```javascript
   if (layoutType === "mynewlayout") {
       // Your layout algorithm
   }
   ```

3. **Test with sample data**

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

### Quick Test

```bash
# Run linter
npm run lint

# Fix linting issues
npm run lint -- --fix
```

### Manual Testing Checklist

- [ ] Trace current file
- [ ] Trace selected function
- [ ] Show visualization
- [ ] Change layouts (all 9)
- [ ] Adjust spacing
- [ ] Toggle physics
- [ ] Export JSON
- [ ] Clear trace data
- [ ] Auto-trace on save
- [ ] Module filtering

## Debugging Tips

### Extension Not Loading

**Check:**
1. `package.json` syntax is valid
2. `main` field points to `extension.js`
3. `activationEvents` are correct
4. No syntax errors in `extension.js`

**View errors:**
- Help → Toggle Developer Tools
- Console tab shows errors

### Python Execution Fails

**Debug Python script:**
```javascript
// In extension.js, add logging:
console.log('Python command:', pythonCommand);
console.log('Python stdout:', stdout);
console.log('Python stderr:', stderr);
```

**Test Python directly:**
```bash
cd /path/to/test/file
python3 .callflow_trace_temp.py
```

### Webview Not Showing

**Check:**
1. `visualizationPanel` is created
2. HTML content is generated
3. No JavaScript errors in webview
4. vis.js CDN is accessible

**Debug webview:**
```javascript
// Add to webview HTML:
console.log('Webview loaded');
console.log('Nodes:', nodes);
console.log('Network:', window.network);
```

View in: DevTools → Console (in Dev Host)

### Performance Issues

**Profile extension:**
1. Help → Toggle Developer Tools
2. Performance tab
3. Record while using extension
4. Analyze bottlenecks

**Optimize:**
- Use async/await for I/O
- Cache trace data
- Debounce auto-trace
- Lazy load webview content

## Code Style

### ESLint Configuration

```bash
# Check code style
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

### Formatting Guidelines

- **Indentation:** 4 spaces
- **Quotes:** Single quotes for strings
- **Semicolons:** Required
- **Line length:** Max 100 characters
- **Naming:**
  - Functions: `camelCase`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Comments

```javascript
/**
 * Function description
 * @param {string} param1 - Parameter description
 * @returns {Promise<void>}
 */
async function myFunction(param1) {
    // Implementation
}
```

## Building for Production

### 1. Update Version

Edit `package.json`:
```json
{
  "version": "1.0.1"
}
```

Update `CHANGELOG.md`:
```markdown
## [1.0.1] - 2025-10-07
### Fixed
- Bug fix description
```

### 2. Run Tests

```bash
npm run lint
npm test
```

### 3. Package Extension

```bash
vsce package
# Creates: callflow-tracer-1.0.1.vsix
```

### 4. Test VSIX

```bash
# Install in clean VS Code
code --install-extension callflow-tracer-1.0.1.vsix

# Test all features
# Uninstall when done
```

### 5. Publish (Future)

```bash
# Get Personal Access Token from Azure DevOps
# https://dev.azure.com/

# Login
vsce login <publisher-name>

# Publish
vsce publish
```

## Contributing

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make changes and commit**
   ```bash
   git add .
   git commit -m "Add my new feature"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

5. **Create Pull Request** on GitHub

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Example:**
```
feat: Add radial tree layout

Implement BFS-based radial tree layout algorithm
with configurable spacing and depth visualization.

Closes #123
```

## Resources

### VS Code Extension Development
- [Extension API](https://code.visualstudio.com/api)
- [Extension Guides](https://code.visualstudio.com/api/extension-guides/overview)
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)

### Tools
- [vsce](https://github.com/microsoft/vscode-vsce) - Extension packaging
- [yo code](https://github.com/microsoft/vscode-generator-code) - Extension generator
- [ESLint](https://eslint.org/) - Linting

### CallFlow Tracer
- [Python Package](https://github.com/rajveer/callflow-tracer)
- [Documentation](https://github.com/rajveer/callflow-tracer/docs)
- [vis.js](https://visjs.org/) - Graph visualization

## Troubleshooting Development

### Node Modules Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### VS Code Extension Host Crashes

1. Close all VS Code windows
2. Clear extension cache:
   ```bash
   rm -rf ~/.vscode/extensions/callflow-tracer-*
   ```
3. Restart VS Code
4. Reload extension

### Can't Debug

1. Check `.vscode/launch.json` exists
2. Verify configuration:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Run Extension",
         "type": "extensionHost",
         "request": "launch",
         "args": ["--extensionDevelopmentPath=${workspaceFolder}"]
       }
     ]
   }
   ```

## Getting Help

- **Issues:** https://github.com/rajveer/callflow-tracer/issues
- **Discussions:** https://github.com/rajveer/callflow-tracer/discussions
- **VS Code Slack:** https://aka.ms/vscode-dev-community

---

**Happy developing! 🚀**
