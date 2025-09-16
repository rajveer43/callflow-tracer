# Publishing Guide for CallFlow Tracer

This guide explains how to publish the callflow-tracer package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org)
2. **Test PyPI Account**: Create an account at [test.pypi.org](https://test.pypi.org)
3. **API Tokens**: Generate API tokens for both PyPI and Test PyPI
4. **Twine Configuration**: Configure twine with your credentials

## Setup

### 1. Install Required Tools

```bash
pip install build twine
```

### 2. Configure Twine

Create `~/.pypirc` file:

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

Replace `your-api-token-here` with your actual API tokens.

## Publishing Process

### 1. Update Version (if needed)

```bash
python version.py 1.0.0
```

### 2. Test Locally

```bash
python test_example.py
```

### 3. Build Package

```bash
python build.py
```

This will:
- Clean previous builds
- Install build dependencies
- Build the package (wheel and source distribution)
- Check the package with twine

### 4. Test on Test PyPI (Recommended)

```bash
python publish.py
# Choose option 1 for Test PyPI
```

Then test the package:

```bash
pip install --index-url https://test.pypi.org/simple/ callflow-tracer
```

### 5. Publish to PyPI

```bash
python publish.py
# Choose option 2 for PyPI
```

## Manual Publishing

If you prefer to publish manually:

```bash
# Build
python -m build

# Check
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Post-Publishing

1. **Verify on PyPI**: Check https://pypi.org/project/callflow-tracer/
2. **Test Installation**: `pip install callflow-tracer`
3. **Update GitHub**: Push changes and create a release
4. **Announce**: Share the package with the community!

## Troubleshooting

### Common Issues

1. **Package already exists**: Update version number
2. **Authentication failed**: Check API tokens in ~/.pypirc
3. **Build failed**: Check pyproject.toml syntax
4. **Upload failed**: Check network connection and PyPI status

### Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in both pyproject.toml and __init__.py
- Test thoroughly before publishing
- Consider using pre-release versions (e.g., 1.0.0a1)

## Security Notes

- Never commit API tokens to version control
- Use environment variables for sensitive data
- Regularly rotate API tokens
- Use Test PyPI for testing before production uploads

## Support

If you encounter issues:
- Check PyPI status: https://status.python.org/
- Review PyPI documentation: https://packaging.python.org/
- Open an issue on GitHub
