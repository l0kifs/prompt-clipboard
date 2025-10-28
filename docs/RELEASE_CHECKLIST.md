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

- [ ] Commit all changes: `git commit -m "chore: bump version to X.Y.Z"`
- [ ] Push to develop: `git push origin develop`
- [ ] Merge to main: `git checkout main && git merge develop`
- [ ] Push main: `git push origin main`
- [ ] Create tag: `git tag vX.Y.Z`
- [ ] Push tag: `git push origin vX.Y.Z`

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

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Notes

- Always test installation from PyPI before announcing
- Keep PyPI credentials secure
- Document any manual steps required
- Update this checklist as the process evolves
