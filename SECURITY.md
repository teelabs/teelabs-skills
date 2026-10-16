# Security policy

Skills are instructions executed by AI-assisted coding tools. A malicious or
carelessly written skill can cause prompt injection, unsafe commands,
credential exposure, data loss, or supply-chain harm.

## Report a vulnerability

Do not open a public issue for an exploitable report. Use GitHub’s private
security advisory feature for this repository when available. If it is not
available, contact the repository maintainers through a private channel listed
on the organization profile and include `skills security report` in the
subject.

Include:

- the affected skill slug and commit or release;
- a concise description and reproducible steps that do not contain secrets;
- the observed impact and any safe mitigation; and
- sanitized logs or files needed to confirm the issue.

Never send passwords, API keys, tokens, private customer data, or live
destructive commands in a report. If credentials may have been exposed, revoke
or rotate them immediately and then report the incident.

## What to report

Please report prompt-injection paths, unsafe or destructive command defaults,
credential or sensitive-data handling, malicious links or downloads, and
dependency or distribution tampering. Maintainers will acknowledge reports,
coordinate a fix, and publish an appropriate advisory when disclosure is safe.

For non-sensitive mistakes, use the relevant issue template and omit all
secrets.
