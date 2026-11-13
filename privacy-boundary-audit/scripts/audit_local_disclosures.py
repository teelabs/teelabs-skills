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
    ("posix-home", re.compile(r"(?i)(?<!file://)(?<![A-Z]:)(?<![\w.])/(?:home|Users|root)/[A-Za-z0-9._-]+(?:/[^\s`\"'<>]*)?")),
    ("windows-profile", re.compile(r"(?i)(?<![\w])[A-Z]:\\Users\\[^\\\s`\"'<>]+(?:\\[^\s`\"'<>]*)?")),
    ("home-file-uri", re.compile(r"(?i)file:///(?:[A-Z]:/Users/|(?:home|Users|root)/)[^\s`\"'<>]+")),
    ("home-shortcut", re.compile(r"(?<![\w])~(?:[A-Za-z0-9._-]+)?/(?:[^\s`\"'<>]+)?")),
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
            if pattern.search(line):
                findings.append((line_number, category))
    return findings


def format_findings(source_name: str, findings: Iterable[tuple[int, str]]) -> str:
    """Format locations and categories without copying source values."""
    safe_name = source_name if re.fullmatch(r"(?:staged|file)-\d+|stdin", source_name) else "source"
    return "\n".join(f"{safe_name}:{line} candidate={category}" for line, category in findings)


def decode_text(blob: bytes) -> str | None:
    """Decode supported text formats, or return None so callers fail closed."""
    if blob.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return blob.decode("utf-16")
        except UnicodeDecodeError:
            return None
    try:
        return blob.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def staged_files() -> list[str | None]:
    """Read complete staged blobs so unchanged sensitive lines are included."""
    changed = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z"],
        check=True,
        capture_output=True,
    )
    changed_paths = {path for path in changed.stdout.split(b"\0") if path}
    if not changed_paths:
        return []
    result = subprocess.run(
        ["git", "ls-files", "--stage", "-z"],
        check=True,
        capture_output=True,
    )
    contents: list[str | None] = []
    found_paths: set[bytes] = set()
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            header, path = record.split(b"\t", 1)
            _mode, object_id, _stage = header.split()
        except ValueError:
            contents.append(None)
            continue
        if path not in changed_paths:
            continue
        found_paths.add(path)
        blob = subprocess.run([b"git", b"cat-file", b"blob", object_id], capture_output=True)
        contents.append(decode_text(blob.stdout) if blob.returncode == 0 else None)
    contents.extend(None for _ in changed_paths - found_paths)
    return contents


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true", help="scan complete staged file contents from the Git index")
    mode.add_argument("--stdin", action="store_true", help="scan prepared GitHub text from standard input")
    mode.add_argument("--files", nargs="+", type=pathlib.Path, help="scan documents or other text files")
    args = parser.parse_args(argv)

    try:
        if args.staged:
            sources = [(f"staged-{index}", content) for index, content in enumerate(staged_files(), start=1)]
        elif args.stdin:
            sources = [("stdin", decode_text(sys.stdin.buffer.read()))]
        else:
            sources = [(f"file-{index}", decode_text(path.read_bytes())) for index, path in enumerate(args.files, start=1)]
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Unable to complete disclosure scan ({type(error).__name__}).", file=sys.stderr)
        return 2

    total = 0
    for name, source in sources:
        if source is None:
            total += 1
            print(f"{name} candidate=unscanned-encoding")
            continue
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
