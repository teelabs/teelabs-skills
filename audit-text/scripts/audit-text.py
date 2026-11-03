#!/usr/bin/env python3
"""Audit GitHub text for literal escaped line breaks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Iterable


ESCAPED_RETURN = re.compile(r"\\(?:r\n|n|r)")
QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    issues(first: 100, states: [OPEN, CLOSED]) {
      nodes { number body comments(first: 100) { nodes { body } } }
    }
    pullRequests(first: 100, states: [OPEN, CLOSED, MERGED]) {
      nodes {
        number body
        comments(first: 100) { nodes { body } }
        reviews(first: 100) { nodes { body } }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class Finding:
    source: str
    count: int
    lines: tuple[int, ...]


def find_escaped_returns(text: str) -> tuple[int, tuple[int, ...]]:
    matches = list(ESCAPED_RETURN.finditer(text))
    lines = tuple(sorted({text.count("\n", 0, match.start()) + 1 for match in matches}))
    return len(matches), lines


def audit_text(text: str, source: str) -> Finding | None:
    count, lines = find_escaped_returns(text)
    return Finding(source, count, lines) if count else None


def run_gh(args: list[str]) -> str:
    try:
        result = subprocess.run(["gh", *args], check=False, capture_output=True, text=True)
    except OSError as error:
        raise RuntimeError("gh CLI is required for remote mode") from error
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"gh failed: {' '.join(args)}")
    return result.stdout


def repository_name(explicit: str | None) -> str:
    value = explicit or run_gh(
        ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]
    ).strip()
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", value):
        raise RuntimeError(f"invalid repository: {value!r}; expected owner/repo")
    return value


def remote_texts(repo: str) -> Iterable[tuple[str, str]]:
    owner, name = repo.split("/", 1)
    raw = run_gh(
        [
            "api", "graphql", "-f", f"query={QUERY}",
            "-F", f"owner={owner}", "-F", f"name={name}",
        ]
    )
    try:
        response: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"gh returned invalid JSON: {error}") from error
    if response.get("errors"):
        raise RuntimeError(json.dumps(response["errors"], ensure_ascii=False))
    repository = response.get("data", {}).get("repository")
    if repository is None:
        raise RuntimeError(f"repository not found or inaccessible: {repo}")

    for issue in repository.get("issues", {}).get("nodes", []):
        number = issue.get("number", "?")
        yield f"{repo} issue #{number} body", issue.get("body") or ""
        for index, comment in enumerate(issue.get("comments", {}).get("nodes", []), 1):
            yield f"{repo} issue #{number} comment {index}", comment.get("body") or ""
    for pull_request in repository.get("pullRequests", {}).get("nodes", []):
        number = pull_request.get("number", "?")
        yield f"{repo} PR #{number} body", pull_request.get("body") or ""
        for index, comment in enumerate(pull_request.get("comments", {}).get("nodes", []), 1):
            yield f"{repo} PR #{number} comment {index}", comment.get("body") or ""
        for index, review in enumerate(pull_request.get("reviews", {}).get("nodes", []), 1):
            yield f"{repo} PR #{number} review {index}", review.get("body") or ""


def report(findings: Iterable[Finding]) -> int:
    total = 0
    for finding in findings:
        total += finding.count
        print(
            f"{finding.source}: found {finding.count} literal escaped return(s) "
            f"on line(s) {', '.join(map(str, finding.lines))}. Use actual line breaks.",
            file=sys.stderr,
        )
    return total


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="audit-text", description="Find literal escaped line breaks in GitHub text."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--stdin", action="store_true", help="audit text read from stdin")
    modes.add_argument(
        "--remote", nargs="?", const="", metavar="OWNER/REPO",
        help="audit GitHub issues and pull requests",
    )
    args = parser.parse_args()

    try:
        if args.stdin:
            findings = [audit_text(sys.stdin.read(), "stdin")]
            repo = None
        else:
            repo = repository_name(args.remote or None)
            findings = [audit_text(text, source) for source, text in remote_texts(repo)]
    except RuntimeError as error:
        print(f"audit-text: {error}", file=sys.stderr)
        return 2

    total = report(finding for finding in findings if finding is not None)
    if total:
        print(f"GitHub text audit failed with {total} literal escaped return(s).", file=sys.stderr)
        return 1
    print(f"GitHub text audit passed for {'stdin' if repo is None else repo}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
