---
description: >-
  Manage SEMVER versions and Keep a Changelog entries across all
  version-tracking files
tags: []
skill: version-changelog
triggers:
  - changelog
  - version bump
  - update changelog
  - semver
  - release notes
name: version-changelog
---
# Version and Changelog Management Skill

This skill ensures consistent version management and changelog tracking across all project files that reference versions.

## When to Use

Invoke this skill when:
1. Making a meaningful change that should be documented
2. The user requests a commit (to bump version if needed)
3. Updating version numbers across the project
4. Adding changelog entries

## Core Principles

1. **SEMVER (Semantic Versioning)**: All projects use MAJOR.MINOR.PATCH
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes (backward compatible)

2. **Keep a Changelog**: Maintain CHANGELOG.md with:
   - `[Unreleased]` section for ongoing work
   - Dated version sections when releasing
   - Categories: Added, Changed, Deprecated, Removed, Fixed, Security

## Workflow

### On Meaningful Changes (Not Yet Committing)

1. **Identify the change type** from the work done:
   - Breaking change → will need MAJOR bump
   - New feature → will need MINOR bump  
   - Bug fix → will need PATCH bump
   - Documentation/chore → may not need version bump

2. **Update CHANGELOG.md** under `[Unreleased]`:
   ```markdown
   ## [Unreleased]
   
   ### Added
   - New feature description
   
   ### Changed
   - Modified behavior description
   
   ### Fixed
   - Bug fix description
   ```

3. Keep changes under `[Unreleased]` until a commit/release is requested.

### On Commit Request (Version Bump)

1. **Determine version bump** from unreleased changes:
   - Any "Removed" or breaking changes → MAJOR
   - Any "Added" features → MINOR
   - Only "Fixed" or "Security" → PATCH
   - Only "Changed" (non-breaking) or docs → PATCH or no bump

2. **Calculate new version**:
   - Read current version from primary source (package.json, CHANGELOG.md, or version file)
   - Apply SEMVER rules
   - Example: 1.2.3 + MINOR → 1.3.0

3. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]
   
   ## [1.3.0] - 2026-08-27
   
   ### Added
   - Feature that was under Unreleased
   ```

4. **Find and update ALL version-tracking files**:
   - `package.json` and `package-lock.json`
   - OpenAPI specs (look for `version:` in YAML/JSON)
   - AsyncAPI specs
   - `pom.xml`, `build.gradle`, `Cargo.toml`, `pyproject.toml`, etc.
   - Dockerfile LABELs (`version=`)
   - Helm charts (`Chart.yaml`)
   - Version badges in README.md
   - Any `VERSION` or `version.txt` files
   - Diagrams with version labels (PlantUML, Mermaid with version annotations)
   - API documentation files
   - Configuration files with version fields

5. **Search strategy for version files**:
   ```bash
   # Find potential version-tracking files
   find . -type f \( \
     -name 'package*.json' -o \
     -name '*openapi*.yaml' -o -name '*openapi*.yml' -o -name '*openapi*.json' -o \
     -name '*asyncapi*.yaml' -o -name '*asyncapi*.yml' -o -name '*asyncapi*.json' -o \
     -name 'swagger*.yaml' -o -name 'swagger*.yml' -o -name 'swagger*.json' -o \
     -name 'pom.xml' -o -name 'build.gradle' -o -name 'Cargo.toml' -o \
     -name 'pyproject.toml' -o -name 'setup.py' -o \
     -name 'Chart.yaml' -o -name 'values.yaml' -o \
     -name 'Dockerfile*' -o -name 'VERSION' -o -name 'version.txt' -o \
     -name '*.puml' -o -name '*.plantuml' -o -name '*.mmd' \
   \) -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/build/*'
   ```

6. **Update each file** with new version:
   - Parse the file format correctly
   - Update version field while preserving formatting
   - For specs, update both root version and any version tags

7. **Report** what was updated:
   ```
   Version bumped: 1.2.3 → 1.3.0 (MINOR)
   
   Updated files:
   - CHANGELOG.md
   - package.json
   - package-lock.json
   - docs/api/openapi.yaml
   - README.md (badge)
   ```

## Implementation Steps

1. **First time in a project**: Scan for all version-tracking files and cache the list
   
2. **On meaningful work**: Ask "Should this go in the changelog?" If yes, update CHANGELOG.md [Unreleased]

3. **On commit request**: 
   - Read unreleased changes
   - Determine bump type
   - Calculate new version
   - Update all version files
   - Move changelog entries from [Unreleased] to dated section
   - Proceed with commit

## File Format Handlers

### package.json
```json
{
  "version": "X.Y.Z"
}
```

### package-lock.json
```json
{
  "version": "X.Y.Z",
  "packages": {
    "": {
      "version": "X.Y.Z"
    }
  }
}
```

### OpenAPI/Swagger YAML
```yaml
openapi: 3.0.0
info:
  version: X.Y.Z
```

### AsyncAPI YAML
```yaml
asyncapi: 2.0.0
info:
  version: X.Y.Z
```

### Cargo.toml
```toml
[package]
version = "X.Y.Z"
```

### pyproject.toml
```toml
[project]
version = "X.Y.Z"
```

### Helm Chart.yaml
```yaml
version: X.Y.Z
appVersion: "X.Y.Z"
```

### Dockerfile
```dockerfile
LABEL version="X.Y.Z"
```

### README.md badges
```markdown
![Version](https://img.shields.io/badge/version-X.Y.Z-blue)
```

## Edge Cases

1. **No CHANGELOG.md exists**: Create one with proper format
2. **First version**: Start at 0.1.0 or 1.0.0 based on project maturity
3. **Multiple package.json files** (monorepo): Update all or ask which to update
4. **Version mismatch across files**: Report and ask which is authoritative
5. **Non-standard version formats**: Report and skip automatic update

## When NOT to Update

- Documentation-only changes (unless project documents versions in docs)
- CI/CD configuration changes
- Test-only changes
- Refactoring without behavior change (unless project policy differs)

Ask the user if unsure whether a change warrants a changelog entry.

## Output Format

Always show:
1. Change type identified (MAJOR/MINOR/PATCH)
2. Version transition (old → new)
3. List of files updated
4. Changelog entry that was added/moved

## Integration with Commit Flow

When the user says "commit this" or similar:
1. Run this skill first
2. Update versions and changelog
3. Then proceed with git commit
4. Use the changelog entry in the commit message

## Example Interaction

```
User: "I've added a new authentication method"
