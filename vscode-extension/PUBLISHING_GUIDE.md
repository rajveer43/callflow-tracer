# VS Code Extension Publishing Guide

## Prerequisites

Before publishing, you need:
1. A Microsoft account
2. An Azure DevOps organization
3. A Personal Access Token (PAT)

## Step 1: Create Icon (Required)

You have two options:

### Option A: Install Pillow and create icon
```bash
pip install Pillow
python -c "from PIL import Image, ImageDraw; img = Image.new('RGB', (128, 128), color='#007ACC'); draw = ImageDraw.Draw(img); draw.ellipse([32, 16, 48, 32], fill='white'); draw.ellipse([16, 56, 32, 72], fill='white'); draw.ellipse([80, 56, 96, 72], fill='white'); draw.ellipse([48, 96, 64, 112], fill='white'); draw.line([(40, 32), (24, 56)], fill='white', width=3); draw.line([(40, 32), (88, 56)], fill='white', width=3); draw.line([(24, 72), (56, 96)], fill='white', width=3); draw.line([(88, 72), (56, 96)], fill='white', width=3); img.save('images/icon.png'); print('Icon created')"
```

### Option B: Temporarily remove icon requirement
Edit `package.json` and remove line 7:
```json
"icon": "images/icon.png",
```

## Step 2: Install vsce (VS Code Extension Manager)

```bash
npm install -g @vscode/vsce
```

## Step 3: Create Publisher Account

1. Go to https://marketplace.visualstudio.com/manage
2. Sign in with your Microsoft account
3. Click "Create publisher"
4. Fill in the details:
   - **Publisher ID**: `rajveer-rathod` (must match package.json)
   - **Display Name**: Your name or company
   - **Email**: Your email

## Step 4: Get Personal Access Token (PAT)

1. Go to https://dev.azure.com/
2. Click on your profile icon → "Personal access tokens"
3. Click "New Token"
4. Configure:
   - **Name**: "VS Code Extension Publishing"
   - **Organization**: All accessible organizations
   - **Expiration**: 90 days (or custom)
   - **Scopes**: Select "Marketplace" → Check "Manage"
5. Click "Create" and **COPY THE TOKEN** (you won't see it again!)

## Step 5: Login to vsce

```bash
vsce login rajveer-rathod
```

When prompted, paste your Personal Access Token.

## Step 6: Package the Extension

```bash
cd vscode-extension
vsce package
```

This creates a `.vsix` file (e.g., `callflow-tracer-1.0.0.vsix`)

## Step 7: Test the Package Locally (Optional)

Install the `.vsix` file in VS Code:
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Click "..." menu → "Install from VSIX..."
4. Select your `.vsix` file
5. Test the extension

## Step 8: Publish to Marketplace

```bash
vsce publish
```

Or publish a specific version:
```bash
vsce publish minor  # Increments to 1.1.0
vsce publish major  # Increments to 2.0.0
vsce publish patch  # Increments to 1.0.1
```

## Step 9: Verify Publication

1. Go to https://marketplace.visualstudio.com/
2. Search for "CallFlow Tracer"
3. Your extension should appear within 5-10 minutes

## Updating the Extension

When you make changes:

1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Run `vsce publish` again

## Troubleshooting

### Error: "Missing publisher name"
- Ensure `"publisher": "rajveer-rathod"` is in package.json
- Ensure you've created a publisher with that exact ID

### Error: "Missing README.md"
- Already created ✓

### Error: "Missing LICENSE"
- Already exists ✓

### Error: "Icon not found"
- Create icon.png using Option A above
- Or remove icon line from package.json

### Error: "Authentication failed"
- Your PAT may have expired
- Create a new PAT and login again with `vsce login rajveer-rathod`

## Quick Command Reference

```bash
# Install vsce
npm install -g @vscode/vsce

# Login
vsce login rajveer-rathod

# Package only (creates .vsix)
vsce package

# Publish
vsce publish

# Unpublish (careful!)
vsce unpublish rajveer-rathod.callflow-tracer

# Show extension info
vsce show rajveer-rathod.callflow-tracer
```

## Important Notes

- **Publisher ID** in package.json must match your marketplace publisher ID
- **Repository URL** should be your actual GitHub repo
- The extension will be available at: `https://marketplace.visualstudio.com/items?itemName=rajveer-rathod.callflow-tracer`
- Users can install with: `code --install-extension rajveer-rathod.callflow-tracer`
