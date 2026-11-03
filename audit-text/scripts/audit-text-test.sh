#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
AUDIT="$ROOT_DIR/scripts/audit-text.py"
TEST_ROOT=$(mktemp -d /tmp/audit-text-test.XXXXXX)
trap 'rm -rf "$TEST_ROOT"' EXIT

if printf 'body with literal \\n marker\n' | python3 "$AUDIT" --stdin >/dev/null 2>&1; then
  echo 'expected literal escaped return to fail' >&2
  exit 1
fi

printf 'body with an actual\nline break\n' | python3 "$AUDIT" --stdin

mkdir -p "$TEST_ROOT/bin"
cat >"$TEST_ROOT/bin/gh" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
cat <<'JSON'
{"data":{"repository":{"issues":{"nodes":[{"number":7,"body":"clean","comments":{"nodes":[{"body":"comment with \\n marker"}]}}]},"pullRequests":{"nodes":[]}}}}
JSON
EOF
chmod +x "$TEST_ROOT/bin/gh"
if PATH="$TEST_ROOT/bin:$PATH" python3 "$AUDIT" --remote teelabs/example >/dev/null 2>&1; then
  echo 'expected remote escaped return to fail' >&2
  exit 1
fi

cat >"$TEST_ROOT/bin/gh" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
cat <<'JSON'
{"data":{"repository":{"issues":{"nodes":[{"number":7,"body":"clean","comments":{"nodes":[{"body":"clean"}]}}]},"pullRequests":{"nodes":[]}}}}
JSON
EOF
chmod +x "$TEST_ROOT/bin/gh"
PATH="$TEST_ROOT/bin:$PATH" python3 "$AUDIT" --remote teelabs/example

echo 'audit-text tests passed'
