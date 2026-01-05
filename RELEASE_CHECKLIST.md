# DeterminAgent Release Checklist

**Version:** `{VERSION}`  
**Release Date:** `YYYY-MM-DD`  
**Release Manager:** `@your-github-handle`

---

## 📋 Pre-Release Verification

Complete all items before creating a release tag.

### Code Quality

| Check | Command | Status |
|-------|---------|--------|
| ✅ All tests pass | `make test` | ⬜ |
| ✅ Coverage ≥90% | `make test-cov` | ⬜ |
| ✅ Linting passes | `make lint` | ⬜ |
| ✅ Type checking passes | `make typecheck` | ⬜ |
| ✅ No security issues | `make security` | ⬜ |

### Version Sync

| Check | Command | Status |
|-------|---------|--------|
| ✅ Versions match | `make version-check` | ⬜ |
| ✅ CHANGELOG.md updated | Manual review | ⬜ |
| ✅ Version bumped correctly | `poetry run python scripts/bump_version.py {VERSION}` | ⬜ |

### Documentation

| Check | File/Action | Status |
|-------|-------------|--------|
| ✅ README.md current | Review installation & quick start | ⬜ |
| ✅ ARCHITECTURE.md current | Review if API changed | ⬜ |
| ✅ API docs build | `mkdocs build` | ⬜ |
| ✅ Tutorials work | Run `flows/blog/main.py --help` | ⬜ |

### Build Verification

| Check | Command | Status |
|-------|---------|--------|
| ✅ Package builds | `make build` | ⬜ |
| ✅ Install from wheel | `pip install dist/*.whl` | ⬜ |
| ✅ Import works | `poetry run python -c "import determinagent"` | ⬜ |
| ✅ Version correct | `poetry run python -c "print(determinagent.__version__)"` | ⬜ |

---

## 🚀 Release Process

### Step 1: Version Bump
```bash
# Bump version in all files
poetry run python scripts/bump_version.py {VERSION}

# Commit the change
git add pyproject.toml determinagent/__init__.py CHANGELOG.md
git commit -m "chore: bump version to {VERSION}"
```

### Step 2: Create Release Tag
```bash
# Create annotated tag
git tag -a {VERSION} -m "Release {VERSION}"

# Push to remote
git push origin main --tags
```

### Step 3: Monitor CI/CD
- [ ] GitHub Actions `publish.yml` workflow triggered
- [ ] TestPyPI publish successful
- [ ] PyPI publish successful
- [ ] GitHub Release created automatically

### Step 4: Post-Release Verification
```bash
# Verify on PyPI (may take a few minutes)
pip install --upgrade determinagent
poetry run python -c "import determinagent; print(determinagent.__version__)"
```

---

## 🔄 Rollback Procedure

If issues are discovered after release:

```bash
# Delete the tag locally
git tag -d {VERSION}

# Delete the tag on remote
git push origin --delete {VERSION}

# Yank the release on PyPI (if necessary, via pypi.org web UI)
# Note: Yanking hides but doesn't delete the release

# Create a patch version with fixes
poetry run python scripts/bump_version.py {PATCH_VERSION}
```

---

## 📝 Release Notes Template

```markdown
## What's Changed

### ✨ New Features
- Feature description (#PR)

### 🐛 Bug Fixes
- Fix description (#PR)

### 📚 Documentation
- Doc updates (#PR)

### 🏗️ Internal
- Refactoring (#PR)

**Full Changelog**: https://github.com/Experto-AI/determinagent/compare/{PREV}...{VERSION}
```

---

## 📊 Release Metrics

| Metric | Value |
|--------|-------|
| Total commits since last release | |
| PRs merged | |
| Contributors | |
| Breaking changes | ⬜ Yes / ✅ No |
| Migration guide needed | ⬜ Yes / ✅ No |

---

*Last updated: 2026-01-04*
