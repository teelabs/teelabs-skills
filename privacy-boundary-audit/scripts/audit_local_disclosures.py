#!/usr/bin/env python3
"""Find likely machine-specific paths without echoing their values."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from collections.abc import Iterable

PATTERNS = (
    ("posix-home", re.compile(r"(?<![\w.])/(?:home|Users)/[A-Za-z0-9._-]+(?:/[^\s`\"'<>]*)?")),
    ("windows-profile", re.compile(r"(?i)(?<![\w])[A-Z]:\\Users\\[^\\\s`\"'<>]+(?:\\[^\s`\"'<>]*)?")),
    ("home-file-uri", re.compile(r"(?i)file:///(?:home|Users)/[^\s`\"'<>]+")),
    ("home-shortcut", re.compile(r"(?<![\w])~/(?:[^\s`\"'<>]+)")),
    ("home-variable", re.compile(r"(?<![\w])\$\{?HOME\}?(?![\w])")),
    ("working-directory-variable", re.compile(r"(?<![\w])\$\{?PWD\}?(?![\w])")),
    ("account-variable", re.compile(r"(?i)(?<![\w])\$\{?(?:USER|USERNAME)\}?(?![\w])|%USERNAME%")),
    ("host-variable", re.compile(r"(?i)(?<![\w])\$\{?(?:HOSTNAME|COMPUTERNAME)\}?(?![\w])")),
    ("windows-profile-variable", re.compile(r"(?i)%USERPROFILE%")),
    ("temporary-directory-variable", re.compile(r"(?i)(?<![\w])\$\{?TMPDIR\}?(?![\w])")),
    ("xdg-config-variable", re.compile(r"(?i)(?<![\w])\$\{?XDG_CONFIG_HOME\}?(?![\w])")),
    ("windows-temp-variable", re.compile(r"(?i)%TEMP%|%TMP%")),
    ("windows-home-drive-variable", re.compile(r"(?i)%HOMEDRIVE%")),
    ("windows-home-path-variable", re.compile(r"(?i)%HOMEPATH%")),
    ("wsl-user-profile", re.compile(r"(?i)/mnt/[a-z]/Users/[A-Za-z0-9._-]+(?:/[^\s`\"'<>]*)?")),
    ("local-endpoint", re.compile(r"(?i)(?<![\w.-])(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?\b")),
)


def find_candidates(source: str) -> list[tuple[int, str]]:
    """Return line/category pairs, never the matched text itself."""
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        for category, pattern in PATTERNS:
            if category == "posix-home" and re.search(r"(?i)file:///", line):
                continue
            if pattern.search(line):
                findings.append((line_number, category))
    return findings


def format_findings(source_name: str, findings: Iterable[tuple[int, str]]) -> str:
    """Format locations and categories without copying source values."""
    safe_name = source_name if re.fullmatch(r"(?:staged|file)-\d+|stdin", source_name) else "source"
    return "\n".join(f"{safe_name}:{line} candidate={category}" for line, category in findings)


def staged_files() -> list[tuple[str, str]]:
    """Read complete staged blobs so unchanged sensitive lines are included."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        check=True,
        capture_output=True,
    )
    files: list[tuple[str, str]] = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", "replace")
        blob = subprocess.run(["git", "show", f":{path}"], capture_output=True)
        if blob.returncode != 0:
            continue
        try:
            content = blob.stdout.decode("utf-8")
        except UnicodeDecodeError:
            continue
        files.append((path, content))
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true", help="scan complete staged file contents from the Git index")
    mode.add_argument("--stdin", action="store_true", help="scan prepared GitHub text from standard input")
    mode.add_argument("--files", nargs="+", type=pathlib.Path, help="scan documents or other text files")
    args = parser.parse_args(argv)

    try:
        if args.staged:
            sources = [(f"staged-{index}", content) for index, (_, content) in enumerate(staged_files(), start=1)]
        elif args.stdin:
            sources = [("stdin", sys.stdin.read())]
        else:
            sources = [(f"file-{index}", path.read_text(errors="replace")) for index, path in enumerate(args.files, start=1)]
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Unable to complete disclosure scan ({type(error).__name__}).", file=sys.stderr)
        return 2

    total = 0
    for name, source in sources:
        numbered = find_candidates(source)
        if numbered:
            total += len(numbered)
            print(format_findings(name, numbered))
    if total:
        print(f"Review required: {total} candidate(s); matched values were withheld.")
        return 1
    print("No local-environment path candidates found; continue with the private-to-public scope review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
