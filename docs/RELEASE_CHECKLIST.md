# Release Checklist

Use this checklist when preparing a new release.

## Pre-Release

- [ ] All tests pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated with all changes
- [ ] Version bumped in `pyproject.toml`
- [ ] No known critical bugs
- [ ] Dependencies are up to date

## Version Update

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `src/prompt_clipboard/config/settings.py` (if hardcoded)
- [ ] Update `CHANGELOG.md` with release date
- [ ] Update any version references in documentation

## Testing

- [ ] Test on Linux
- [ ] Test on macOS (if available)
- [ ] Test on Windows (if available)
- [ ] Test fresh installation: `pip install prompt-clipboard`
- [ ] Test `uvx prompt-clipboard`
- [ ] Verify global hotkey works
- [ ] Test basic CRUD operations
- [ ] Test search functionality
- [ ] Check logs for errors

## Build

- [ ] Clean build artifacts: `rm -rf dist/`
- [ ] Build package: `uv build`
- [ ] Verify build contents
- [ ] Test installation from local build

## Git Operations

**CRITICAL: Tags must be created on `main` branch only!**

- [ ] Commit all changes to develop: `git commit -m "chore: bump version to X.Y.Z"`
- [ ] Push to develop: `git push origin develop`
- [ ] Switch to main: `git checkout main`
- [ ] Merge develop to main: `git merge develop`
- [ ] Push main: `git push origin main`
- [ ] Create tag ON MAIN: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Return to develop: `git checkout develop`

**Why this matters:** The GitHub Actions workflow verifies that tags are on `main` branch. Tags created on `develop` or feature branches will fail the publishing check.

## Publishing

- [ ] Monitor GitHub Actions workflow
- [ ] Verify package appears on PyPI
- [ ] Test installation from PyPI: `pip install prompt-clipboard`
- [ ] Test with uvx: `uvx prompt-clipboard`

## Post-Release

- [ ] Create GitHub Release with changelog
- [ ] Update project-specific PyPI token (after first release)
- [ ] Close related issues and PRs
- [ ] Announce release (if applicable)
- [ ] Update documentation if needed
- [ ] Monitor for issues

## GitHub Release Notes Template

```markdown
## What's New in vX.Y.Z

Brief description of this release.

### ✨ New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 📝 Documentation
- Doc update 1

### 🔧 Technical Changes
- Internal change 1

## Installation

\`\`\`bash
pip install prompt-clipboard
# or
uvx prompt-clipboard
\`\`\`

## Full Changelog

See [CHANGELOG.md](https://github.com/l0kifs/prompt-clipboard/blob/main/CHANGELOG.md) for complete details.
```

## Rollback Procedure

If issues are discovered after release:

1. Identify the problem severity
2. If critical:
   - Mark release as draft/pre-release on GitHub
   - Consider yanking from PyPI (only for serious issues)
   - Prepare hotfix release
3. If non-critical:
   - Document in issues
   - Fix in next release

### If Tag Was Created on Wrong Branch

If you accidentally created a tag on `develop` instead of `main`:

```fish
# 1. Delete the incorrect tag
git tag -d vX.Y.Z
git push --delete origin vX.Y.Z

# 2. Merge to main
git checkout main
git merge develop
git push origin main

# 3. Recreate tag on main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z

# 4. Return to develop
git checkout develop
```

**Note:** If the package was already published to PyPI, you cannot re-upload the same version. In this case, you'll need to increment to the next patch version (e.g., 0.1.0 → 0.1.1).

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Notes

- **Always create tags on `main` branch** - GitHub Actions workflow enforces this
- Always test installation from PyPI before announcing
- Keep PyPI credentials secure
- Document any manual steps required
- Update this checklist as the process evolves
- If workflow fails with "tag not on main" error, see Rollback Procedure above
