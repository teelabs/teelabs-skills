# Contributing

Thanks for improving the Teelabs skill collection.

## Add or change a skill

1. Create or edit one top-level skill directory with a `SKILL.md`.
2. Use YAML frontmatter with a unique lowercase hyphenated `name` matching the
   directory and a concise model-facing `description` explaining when it
   applies.
3. Keep the core skill portable. Put optional detail in `references/` or
   `examples/` and link to it with paths relative to the Markdown file.
4. Update `skills.json` and `CHANGELOG.md` when the public collection changes.
5. Do not include secrets, credentials, destructive defaults, or hidden
   external side effects.

## Review and checks

Before opening a pull request, inspect the complete diff and run:

```sh
node scripts/validate-skills.mjs
git diff --check
```

Also run any focused tests relevant to the skill. Reviewers should check
instruction safety, portability, links, frontmatter, and independent install
and update behavior. Do not paste credentials, private prompts, or other
sensitive data into issues or pull requests.

## Pull requests

Keep each pull request focused on one skill or one collection concern. Explain
the affected skill slug, user-visible behavior, verification commands, and any
known installer-specific limitation. A maintainer must review changes before
merge.
