# Publishing Steps: VS Code Extension

---

## Prerequisites

1. **VS Code Account**: Sign in to [Visual Studio Marketplace](https://marketplace.visualstudio.com/)
2. **Personal Access Token**: Get from [Azure DevOps](https://dev.azure.com/rajveer43/_usersSettings/tokens)
3. **vsce CLI**: Install the Visual Studio Code Extension CLI
   ```bash
   npm install -g @vscode/vsce
   ```

---

## Step 1: Prepare Extension

### 1.1 Update Version
```bash
cd vscode-extension
npm version patch  # Updates to 2.1.1
```

### 1.2 Update Changelog
Edit `CHANGELOG.md`:
```markdown
## [2.1.1] - 2025-04-17

### Fixed
- Updated marketplace links to correct publisher (rajveer43)
- Fixed README installation instructions
```

### 1.3 Compile Extension
```bash
npm run compile
```

### 1.4 Test Locally
```bash
# Package and install locally
npx vsce package
code --install-extension callflow-tracer-2.1.1.vsix
```

---

## Step 2: Configure Publisher

### 2.1 Check package.json
Ensure correct publisher:
```json
{
  "name": "callflow-tracer",
  "publisher": "rajveer43",
  "version": "2.1.1"
}
```

### 2.2 Login to Marketplace
```bash
npx vsce login rajveer43
# Enter your Personal Access Token when prompted
```

---

## Step 3: Publish Extension

### 3.1 Publish to Marketplace
```bash
npx vsce publish
```

### 3.2 Verify Publication
Check: https://marketplace.visualstudio.com/items?itemName=rajveer43.callflow-tracer

---

## Alternative: Publish from CI/CD

### GitHub Actions Workflow
Create `.github/workflows/publish.yml`:

```yaml
name: Publish VS Code Extension

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        working-directory: vscode-extension
        
      - name: Compile extension
        run: npm run compile
        working-directory: vscode-extension
        
      - name: Publish to VS Code Marketplace
        run: npx vsce publish
        working-directory: vscode-extension
        env:
          VSCE_PAT: ${{ secrets.VSCE_PAT }}
```

### Set up GitHub Secret
1. Go to repository Settings > Secrets and variables > Actions
2. Add `VSCE_PAT` with your Personal Access Token

---

## Step 4: Post-Publishing

### 4.1 Update Documentation
- Update README with new version
- Update main project README
- Announce on social media

### 4.2 Test Installation
```bash
# Test fresh install
code --install-extension rajveer43.callflow-tracer
```

### 4.3 Check Extension Page
Verify all details on marketplace page:
- Screenshots
- Description
- Categories
- Pricing (Free)

---

## Troubleshooting

### Common Issues

1. **Publisher Mismatch**
   ```
   Error: Publisher 'rajveer' does not match 'rajveer43'
   ```
   **Fix**: Update `package.json` publisher field

2. **Version Already Exists**
   ```
   Error: Version 2.1.1 already exists
   ```
   **Fix**: `npm version patch` to increment version

3. **Invalid Token**
   ```
   Error: 401 Unauthorized
   ```
   **Fix**: Generate new Personal Access Token

4. **Missing Dependencies**
   ```
   Error: Cannot find module 'typescript'
   ```
   **Fix**: `npm install` in vscode-extension directory

### Unpublish (if needed)
```bash
npx vsce unpublish rajveer43.callflow-tracer
```

---

## Quick Reference Commands

```bash
# Development
cd vscode-extension
npm install
npm run compile
code --install-extension callflow-tracer-2.1.1.vsix

# Publishing
npm version patch
npx vsce publish

# Verification
code --install-extension rajveer43.callflow-tracer
```

---

## Publishing Checklist

- [ ] Version updated in package.json
- [ ] CHANGELOG.md updated
- [ ] Extension compiles without errors
- [ ] Local testing successful
- [ ] Publisher configured correctly
- [ ] Marketplace login successful
- [ ] Extension published
- [ ] Marketplace page verified
- [ ] Installation tested

---

## Links

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Visual Studio Marketplace](https://marketplace.visualstudio.com/)
- [vsce CLI Documentation](https://github.com/microsoft/vscode-vsce)
- [Your Extension](https://marketplace.visualstudio.com/items?itemName=rajveer43.callflow-tracer)
