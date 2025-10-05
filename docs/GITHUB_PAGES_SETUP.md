# 📚 Publishing Documentation to GitHub Pages

Complete guide to publish CallFlow Tracer documentation using GitHub Pages.

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository: `https://github.com/rajveer43/callflow-tracer`
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main` (or `master`)
   - **Folder**: `/docs`
5. Click **Save**
6. Wait 1-2 minutes for deployment

Your docs will be live at: `https://rajveer43.github.io/callflow-tracer/`

---

## 📁 Documentation Structure for GitHub Pages

We'll use the existing `/docs` folder with a proper index:

```
docs/
├── index.md                    # Homepage (will be created)
├── _config.yml                 # Jekyll config (will be created)
├── API_DOCUMENTATION.md        # ✅ Already exists
├── FEATURES_COMPLETE.md        # ✅ Already exists
├── INSTALLATION_GUIDE.md       # ✅ Already exists
├── USER_GUIDE.md               # ✅ Already exists
├── INDEX.md                    # ✅ Already exists (rename to navigation.md)
└── assets/                     # Optional: images, css
```

---

## 🚀 Method 1: Using Jekyll (Recommended)

### Step 1: Create `_config.yml`

Create this file in `/docs` folder:

```yaml
# Jekyll configuration for GitHub Pages
theme: jekyll-theme-cayman
title: CallFlow Tracer
description: A comprehensive Python library for tracing, profiling, and visualizing function call flows
baseurl: "/callflow-tracer"
url: "https://rajveer43.github.io"

# Navigation
navigation:
  - title: Home
    url: /
  - title: Installation
    url: /INSTALLATION_GUIDE
  - title: User Guide
    url: /USER_GUIDE
  - title: API Reference
    url: /API_DOCUMENTATION
  - title: Features
    url: /FEATURES_COMPLETE
  - title: GitHub
    url: https://github.com/rajveer43/callflow-tracer

# Markdown settings
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge

# Plugins
plugins:
  - jekyll-relative-links
  - jekyll-optional-front-matter
  - jekyll-readme-index
  - jekyll-titles-from-headings

# Settings
relative_links:
  enabled: true
  collections: true

titles_from_headings:
  enabled: true
  strip_title: true
  collections: true

# Exclude files
exclude:
  - README.md
  - Gemfile
  - Gemfile.lock
```

### Step 2: Create `index.md`

Create homepage in `/docs/index.md`:

```markdown
# CallFlow Tracer Documentation

> A comprehensive Python library for tracing, profiling, and visualizing function call flows with interactive flamegraphs and call graphs.

[![PyPI version](https://badge.fury.io/py/callflow-tracer.svg)](https://badge.fury.io/py/callflow-tracer)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

# Trace your code
with trace_scope() as graph:
    my_function()

# Generate flamegraph
generate_flamegraph(
    graph,
    "flamegraph.html",
    color_scheme="performance"  # Green=fast, Red=slow
)
```

## 📚 Documentation

### Getting Started
- [Installation Guide](INSTALLATION_GUIDE.md) - Setup and configuration
- [User Guide](USER_GUIDE.md) - Complete usage guide
- [Quick Test](../QUICK_TEST.md) - Fast verification

### Reference
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Features Documentation](FEATURES_COMPLETE.md) - All features explained
- [Navigation Index](navigation.md) - Documentation index

### Feature Guides
- [Enhanced Features](../ENHANCED_FEATURES.md) - New features
- [Flamegraph Guide](../examples/FLAMEGRAPH_README.md) - Flamegraph documentation
- [Jupyter Guide](../examples/JUPYTER_README.md) - Jupyter integration

## ✨ Key Features

### 🔥 Enhanced Flamegraph
- **Statistics Panel**: See total functions, calls, execution time, and bottlenecks
- **5 Color Schemes**: Default, Hot, Cool, Rainbow, and Performance
- **Search Functionality**: Find specific functions quickly
- **SVG Export**: High-quality vector graphics
- **Modern UI**: Responsive design with gradients

### 📊 Performance Profiling
- **CPU Profiling**: cProfile integration with detailed statistics (FIXED!)
- **Memory Tracking**: Current and peak memory usage
- **I/O Wait Time**: Measure time spent waiting
- **Health Indicators**: Visual performance status

### 🎨 Visualization
- **Interactive Call Graphs**: Zoom, pan, explore relationships
- **4 Layout Options**: Hierarchical, Force-Directed, Circular, Timeline
- **Module Filtering**: Focus on specific parts of your code (FIXED!)
- **Rich Tooltips**: Detailed metrics on hover

### 📓 Jupyter Integration
- **Magic Commands**: `%%callflow_cell_trace` for quick tracing
- **Inline Visualizations**: Display interactive graphs in notebooks
- **Full Feature Support**: All features work seamlessly

## 🎯 Use Cases

### Finding Performance Bottlenecks
```python
generate_flamegraph(graph, "bottlenecks.html", color_scheme="performance")
# Wide RED bars = bottlenecks!
```

### Understanding Code Flow
```python
export_html(graph, "flow.html", layout="hierarchical")
# See top-down execution flow
```

### Jupyter Analysis
```python
%%callflow_cell_trace
my_function()
# Interactive graph appears inline!
```

## 📦 Installation

```bash
pip install callflow-tracer
```

## 🔗 Links

- [GitHub Repository](https://github.com/rajveer43/callflow-tracer)
- [PyPI Package](https://pypi.org/project/callflow-tracer/)
- [Issue Tracker](https://github.com/rajveer43/callflow-tracer/issues)
- [Discussions](https://github.com/rajveer43/callflow-tracer/discussions)

## 📞 Support

- 📧 Email: rathodrajveer1311@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/rajveer43/callflow-tracer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/rajveer43/callflow-tracer/discussions)

---

**Happy Tracing! 🎉**
```

### Step 3: Rename INDEX.md

```bash
# Rename to avoid conflict with index.md
mv docs/INDEX.md docs/navigation.md
```

---

## 🎨 Method 2: Using MkDocs (Alternative)

### Step 1: Install MkDocs

```bash
pip install mkdocs mkdocs-material
```

### Step 2: Create `mkdocs.yml` in root

```yaml
site_name: CallFlow Tracer
site_url: https://rajveer43.github.io/callflow-tracer/
site_description: A comprehensive Python library for tracing, profiling, and visualizing function call flows
site_author: Rajveer Rathod
repo_url: https://github.com/rajveer43/callflow-tracer
repo_name: rajveer43/callflow-tracer

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy

nav:
  - Home: index.md
  - Getting Started:
      - Installation: docs/INSTALLATION_GUIDE.md
      - Quick Start: QUICK_TEST.md
      - User Guide: docs/USER_GUIDE.md
  - Features:
      - All Features: docs/FEATURES_COMPLETE.md
      - Enhanced Features: ENHANCED_FEATURES.md
      - Flamegraph Guide: examples/FLAMEGRAPH_README.md
      - Jupyter Integration: examples/JUPYTER_README.md
  - Reference:
      - API Documentation: docs/API_DOCUMENTATION.md
      - Navigation Index: docs/navigation.md
      - Changelog: CHANGELOG.md
  - Examples:
      - Flamegraph Examples: examples/flamegraph_example.py
      - Enhanced Demo: examples/flamegraph_enhanced_demo.py
  - Testing:
      - Testing Guide: TESTING_GUIDE.md
      - Quick Test: QUICK_TEST.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - admonition
  - pymdownx.details
  - pymdownx.tabbed:
      alternate_style: true
  - attr_list
  - md_in_html
  - toc:
      permalink: true

plugins:
  - search
  - git-revision-date-localized

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/rajveer43/callflow-tracer
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/callflow-tracer/
```

### Step 3: Build and Deploy

```bash
# Build documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## 🌐 Method 3: Using Sphinx (Professional)

### Step 1: Install Sphinx

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

### Step 2: Create `conf.py` in `/docs`

```python
# Sphinx configuration
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'CallFlow Tracer'
copyright = '2025, Rajveer Rathod'
author = 'Rajveer Rathod'
release = '0.3.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
```

### Step 3: Build

```bash
cd docs
sphinx-build -b html . _build/html
```

---

## 🚀 Recommended Approach: Jekyll (Simplest)

### Complete Setup Steps

1. **Create `_config.yml` in `/docs`**
2. **Create `index.md` in `/docs`**
3. **Rename `INDEX.md` to `navigation.md`**
4. **Push to GitHub**
5. **Enable GitHub Pages in Settings**

### Commands:

```bash
# Navigate to docs folder
cd docs

# Create _config.yml (copy content from above)
# Create index.md (copy content from above)

# Rename INDEX.md
mv INDEX.md navigation.md

# Commit and push
git add .
git commit -m "Add GitHub Pages documentation"
git push origin main
```

---

## 📝 Custom Domain (Optional)

### Step 1: Create CNAME file

In `/docs` folder:

```bash
echo "docs.callflow-tracer.com" > CNAME
```

### Step 2: Configure DNS

Add these records to your domain:

```
Type: CNAME
Name: docs
Value: rajveer43.github.io
```

### Step 3: Update GitHub Settings

1. Go to Settings → Pages
2. Enter custom domain: `docs.callflow-tracer.com`
3. Check "Enforce HTTPS"

---

## 🎨 Customization

### Add Custom CSS

Create `/docs/assets/css/style.scss`:

```scss
---
---

@import "{{ site.theme }}";

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-content {
  h1, h2, h3, h4, h5, h6 {
    color: #667eea;
  }
  
  code {
    background-color: #f5f5f5;
    border-radius: 3px;
    padding: 2px 5px;
  }
  
  pre {
    background-color: #2d2d2d;
    border-radius: 5px;
  }
}
```

### Add Navigation

Create `/docs/_layouts/default.html`:

```html
<!DOCTYPE html>
<html lang="{{ site.lang | default: "en-US" }}">
  <head>
    <meta charset="UTF-8">
    <title>{{ page.title | default: site.title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{{ '/assets/css/style.css?v=' | append: site.github.build_revision | relative_url }}">
  </head>
  <body>
    <header class="page-header" role="banner">
      <h1 class="project-name">{{ site.title }}</h1>
      <h2 class="project-tagline">{{ site.description }}</h2>
      <a href="{{ site.github.repository_url }}" class="btn">View on GitHub</a>
      <a href="{{ '/INSTALLATION_GUIDE' | relative_url }}" class="btn">Installation</a>
      <a href="{{ '/USER_GUIDE' | relative_url }}" class="btn">User Guide</a>
      <a href="{{ '/API_DOCUMENTATION' | relative_url }}" class="btn">API Docs</a>
    </header>

    <main id="content" class="main-content" role="main">
      {{ content }}

      <footer class="site-footer">
        <span class="site-footer-owner">
          <a href="{{ site.github.repository_url }}">{{ site.github.repository_name }}</a> 
          is maintained by <a href="{{ site.github.owner_url }}">{{ site.github.owner_name }}</a>.
        </span>
      </footer>
    </main>
  </body>
</html>
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] GitHub Pages is enabled in Settings
- [ ] `/docs` folder is selected as source
- [ ] `_config.yml` exists in `/docs`
- [ ] `index.md` exists in `/docs`
- [ ] All markdown files are in `/docs`
- [ ] Site is accessible at `https://rajveer43.github.io/callflow-tracer/`
- [ ] Navigation works
- [ ] Code highlighting works
- [ ] Links are not broken

---

## 🐛 Troubleshooting

### Issue: 404 Page Not Found

**Solution**: 
- Check that `/docs` folder is selected in Settings → Pages
- Ensure `index.md` exists in `/docs`
- Wait 2-3 minutes for deployment

### Issue: Broken Links

**Solution**:
- Use relative links: `[Link](./page.md)` not `[Link](page.md)`
- Update `_config.yml` with correct `baseurl`

### Issue: No Styling

**Solution**:
- Ensure `_config.yml` has `theme: jekyll-theme-cayman`
- Clear browser cache
- Check GitHub Pages build status

### Issue: Code Not Highlighted

**Solution**:
- Use triple backticks with language: ` ```python `
- Ensure `markdown: kramdown` in `_config.yml`

---

## 🚀 Deployment Workflow

### Automatic Deployment (Recommended)

Create `.github/workflows/docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - 'README.md'
      - 'CHANGELOG.md'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
          publish_branch: gh-pages
```

---

## 📊 Analytics (Optional)

### Add Google Analytics

In `_config.yml`:

```yaml
google_analytics: UA-XXXXXXXXX-X
```

### Add GitHub Stats

In `index.md`:

```markdown
![GitHub stars](https://img.shields.io/github/stars/rajveer43/callflow-tracer?style=social)
![GitHub forks](https://img.shields.io/github/forks/rajveer43/callflow-tracer?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/rajveer43/callflow-tracer?style=social)
```

---

## 🎉 Final Steps

1. **Create files** (see above)
2. **Commit and push**:
   ```bash
   git add docs/
   git commit -m "Setup GitHub Pages documentation"
   git push origin main
   ```
3. **Enable GitHub Pages** in Settings
4. **Wait 2-3 minutes**
5. **Visit**: `https://rajveer43.github.io/callflow-tracer/`

---

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)

---

**Your documentation will be live at: `https://rajveer43.github.io/callflow-tracer/`** 🎉

---

*GitHub Pages Setup Guide - Created: 2025-10-05*
