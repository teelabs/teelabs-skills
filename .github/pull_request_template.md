## Summary

- Affected skill slug(s) or collection concern:
- What changed:

## Safety and scope

- [ ] No secrets, credentials, or sensitive data are included.
- [ ] External side effects and destructive operations are explicit and reviewed.
- [ ] The change remains independently installable and updateable by skill slug.
- [ ] Local Markdown links and companion files were checked.

## Verification

Commands run and results:

```text
node scripts/validate-skills.mjs
git diff --check
```

Additional checks:

