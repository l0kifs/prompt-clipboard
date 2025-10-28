# Publishing Guide

This guide explains how to publish `prompt-clipboard` to PyPI so users can install it with `pip` or `uvx`.

## Two Publishing Methods

Choose one of these methods:
- **Method A: GitHub Actions (Recommended)** - Automated, more secure, no local credentials needed
- **Method B: Manual Publishing** - Direct control, requires local setup with API tokens

---

## Method A: Publishing with GitHub Actions (Recommended)

This is the **recommended** approach - more secure and automated.

### Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **uv**: Ensure you have uv installed locally for testing builds

### One-Time Setup

#### Step 1: Create PyPI API Token

Generate an API token at https://pypi.org/manage/account/token/:
- **For first-time publishing**: Create a token with scope "Entire account" (you can't select a specific project that doesn't exist yet)
- Copy the token (it starts with `pypi-...`)

**Note:** After your first successful publish, you can create a project-specific token for better security.

#### Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/l0kifs/prompt-clipboard
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PYPI_API_TOKEN`
5. Value: Paste your PyPI token
6. Click **Add secret**

#### Step 3: Create GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Fetch all history for all branches and tags
    
    - name: Check if tag is on main branch
      run: |
        # Check if the tag points to a commit that is in main branch
        if ! git branch -r --contains ${{ github.ref }} | grep -q 'origin/main'; then
          echo "Error: Tag ${{ github.ref }} is not on main branch"
          exit 1
        fi
    
    - name: Install uv
      uses: astral-sh/setup-uv@v5
      with:
        enable-cache: true
    
    - name: Build package
      run: uv build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

**Important:** This workflow includes a branch check to ensure tags are only published from the `main` branch, preventing accidental releases from `develop` or feature branches.

Commit and push this file:

```fish
mkdir -p .github/workflows
# Create the file with the content above
git add .github/workflows/publish.yml
git commit -m "ci: add PyPI publishing workflow"
git push origin develop
```

#### Step 4: Verify Project Configuration

Ensure `pyproject.toml` has all required metadata:
- Package name
- Version
- Description
- Authors
- License
- URLs
- Classifiers
- Keywords
- Entry point

### Publishing Process (GitHub Actions)

#### Step 1: Update Version

Edit the version in `pyproject.toml`:

```toml
[project]
name = "prompt-clipboard"
version = "0.1.1"  # Increment this
```

Version format: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

#### Step 2: Update Changelog

Update `CHANGELOG.md`:

```markdown
## [0.1.1] - 2025-10-29

### Added
- New feature X
- New feature Y

### Changed
- Improved Z

### Fixed
- Bug fix A
```

#### Step 3: Test Build Locally (Optional but Recommended)

Before pushing a tag, test the build locally:

```fish
# Clean previous builds
rm -rf dist/

# Build the package
uv build
```

This creates:
- `dist/prompt_clipboard-0.1.1-py3-none-any.whl` (wheel)
- `dist/prompt_clipboard-0.1.1.tar.gz` (source distribution)

Test the local build:

```fish
# Install from local wheel
uvx --from ./dist/prompt_clipboard-0.1.1-py3-none-any.whl prompt-clipboard
```

#### Step 4: Commit and Create Tag

**IMPORTANT:** Always create tags on the `main` branch after merging from `develop`.

```fish
# 1. Commit changes to develop
git add .
git commit -m "chore: bump version to 0.1.1"
git push origin develop

# 2. Merge to main - REQUIRED for publishing
git checkout main
git merge develop
git push origin main

# 3. Create and push tag ON MAIN BRANCH
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1

# 4. Return to develop
git checkout develop
```

**Why this matters:** The workflow verifies that tags are created on `main` to prevent accidental releases from development branches. If you create a tag on `develop`, the workflow will fail with an error.

**That's it!** The GitHub Action will automatically:
1. Build the package
2. Publish to PyPI

#### Step 5: Monitor the Workflow

1. Go to https://github.com/l0kifs/prompt-clipboard/actions
2. Watch the "Publish to PyPI" workflow run
3. Check for any errors

#### Step 6: Verify Installation

After the workflow succeeds (wait ~1-2 minutes):

```fish
# Test installation from PyPI
pip install prompt-clipboard
# or
uvx prompt-clipboard
```

#### Step 7: Update to Project-Specific Token (After First Publish)

For better security after your first successful publish:

1. Go to https://pypi.org/manage/project/prompt-clipboard/settings/
2. Scroll to "API tokens"
3. Create new token with scope "Project: prompt-clipboard"
4. Update the `PYPI_API_TOKEN` secret in GitHub:
   - Go to GitHub repo → Settings → Secrets → Actions
   - Edit `PYPI_API_TOKEN` with the new project-specific token
5. Delete the old account-wide token at https://pypi.org/manage/account/token/

### Quick Reference (GitHub Actions Method)

```fish
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md

# 3. Test locally (optional but recommended)
rm -rf dist/ && uv build
uvx --from ./dist/prompt_clipboard-X.Y.Z-py3-none-any.whl prompt-clipboard

# 4. Commit to develop
git add .
git commit -m "chore: bump version to X.Y.Z"
git push origin develop

# 5. Merge to main (REQUIRED)
git checkout main
git merge develop
git push origin main

# 6. Create tag ON MAIN (triggers GitHub Actions)
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z

# 7. Return to develop
git checkout develop

# Done! GitHub Actions will publish to PyPI
```

**Critical:** Always create tags on `main` branch, never on `develop` or feature branches!

---

## Method B: Manual Publishing (Alternative)

Use this method if you prefer direct control or can't use GitHub Actions.

### Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org
2. **API Token**: Generate at https://pypi.org/manage/account/token/
   - For first publish: "Entire account" scope
   - After first publish: Create project-specific token
3. **uv**: Ensure you have uv installed

### One-Time Setup

Create or edit `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

**Security Note:** Keep this token secure! Consider using a project-specific token.

### Publishing Process (Manual)

#### Step 1-2: Update version and changelog (same as Method A)

#### Step 3: Build the Package

```fish
rm -rf dist/
uv build
```

#### Step 4: Publish to PyPI

```fish
uv publish
```

Or with explicit credentials:

```fish
uv publish --username __token__ --password pypi-YOUR_API_TOKEN_HERE
```

#### Step 5: Commit and Tag

```fish
git add .
git commit -m "chore: bump version to X.Y.Z"
git push origin develop
git checkout main
git merge develop
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

#### Step 6: Verify Installation

```fish
pip install prompt-clipboard
# or
uvx prompt-clipboard
```

### Quick Reference (Manual Method)

```fish
# Update version in pyproject.toml, update CHANGELOG.md
rm -rf dist/
uv build
uv publish
git add . && git commit -m "chore: bump version to X.Y.Z"
git push origin develop
git checkout main && git merge develop && git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

---

## Testing on TestPyPI (Optional)

Before publishing to the main PyPI, test on TestPyPI:

### Setup TestPyPI

1. Create account at https://test.pypi.org
2. Generate API token
3. Add to `~/.pypirc`:

```ini
[testpypi]
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

### Publish to TestPyPI

```fish
uv build
uv publish --publish-url https://test.pypi.org/legacy/
```

### Install from TestPyPI

```fish
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ prompt-clipboard
```

---

## Trusted Publishing (More Secure)

Instead of using API tokens, configure trusted publishing:

1. Go to https://pypi.org/manage/project/prompt-clipboard/settings/publishing/
2. Add GitHub as a trusted publisher:
   - Owner: `l0kifs`
   - Repository: `prompt-clipboard`
   - Workflow: `publish.yml`
   - Environment: leave blank or create one

Then update the GitHub workflow to use trusted publishing (remove the password section).

---

## Troubleshooting

### "File already exists" error

You're trying to upload a version that already exists. Increment the version number.

### "Invalid credentials" error

Check your API token in `~/.pypirc` or the command line.

### Build errors

Ensure all dependencies are properly specified in `pyproject.toml`.

### Import errors after installation

Make sure the package structure is correct and `__init__.py` files exist.

### "Invalid package name" error

Package names on PyPI must:
- Use lowercase letters, numbers, and hyphens/underscores
- Not conflict with existing packages
- Follow PEP 508

### "Tag is not on main branch" error

**Cause:** You created a tag on `develop` or another branch instead of `main`.

**Solution:**
```fish
# Delete the incorrect tag
git tag -d vX.Y.Z
git push --delete origin vX.Y.Z

# Merge to main first
git checkout main
git merge develop
git push origin main

# Recreate tag on main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z

# Return to develop
git checkout develop
```

### Workflow succeeds but package not on PyPI

Check the workflow logs - the version might already exist on PyPI. PyPI doesn't allow re-uploading the same version.

---

## Best Practices

1. **Always create tags on `main` branch** - Never tag on `develop` or feature branches
2. **Merge develop to main before tagging** - Ensure all changes are in main
3. **Test on TestPyPI first** (optional but recommended for major releases)
4. **Use semantic versioning** (MAJOR.MINOR.PATCH)
5. **Update CHANGELOG.md** with all changes before release
6. **Test build locally** before pushing tags
7. **Keep credentials secure** - use project-specific tokens
8. **Test installation** from PyPI after publishing
9. **Create GitHub Release** after successful publish
10. **Monitor PyPI stats** and user feedback

---

## Post-Release Checklist

After successful publication:

- [ ] Verify installation: `pip install prompt-clipboard`
- [ ] Test the installed package: `prompt-clipboard --version`
- [ ] Create GitHub Release with changelog
- [ ] Update project documentation if needed
- [ ] Announce on relevant channels (if applicable)
- [ ] Monitor PyPI downloads and issues
- [ ] Update project-specific token (after first release)

---

## Resources

- [PyPI](https://pypi.org)
- [Test PyPI](https://test.pypi.org)
- [uv Publishing Docs](https://docs.astral.sh/uv/guides/publish/)
- [Semantic Versioning](https://semver.org)
- [Python Packaging Guide](https://packaging.python.org/)
