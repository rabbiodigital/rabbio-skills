#!/usr/bin/env bash
# create_passfiles.sh
#
# Create imapsync passfiles for a set of mailboxes.
# Each mailbox needs two files: src_<NAME>.pass and dst_<NAME>.pass
# Passwords are written WITHOUT a trailing newline (printf '%s'), then chmod 600.
#
# Usage:
#   create_passfiles.sh <passdir> <NAME> <SRC_PASS> <DST_PASS> [<NAME> <SRC_PASS> <DST_PASS> ...]
#
# Example:
#   create_passfiles.sh /tmp/imapsync_migration \
#     sales  'src-pw-1'  'dst-pw-1' \
#     office 'src-pw-2'  'dst-pw-2'

set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <passdir> <NAME> <SRC_PASS> <DST_PASS> [<NAME> <SRC_PASS> <DST_PASS> ...]" >&2
  exit 1
fi

PASSDIR="$1"
shift

mkdir -p "$PASSDIR"

# Remaining args must come in triples: NAME SRC_PASS DST_PASS
if [ $(( $# % 3 )) -ne 0 ]; then
  echo "ERROR: arguments after passdir must come in triples (NAME SRC_PASS DST_PASS)" >&2
  exit 1
fi

count=0
while [ "$#" -gt 0 ]; do
  NAME="$1"
  SRC_PASS="$2"
  DST_PASS="$3"
  shift 3

  printf '%s' "$SRC_PASS" > "$PASSDIR/src_${NAME}.pass"
  printf '%s' "$DST_PASS" > "$PASSDIR/dst_${NAME}.pass"
  chmod 600 "$PASSDIR/src_${NAME}.pass" "$PASSDIR/dst_${NAME}.pass"

  count=$((count + 1))
  echo "Created passfiles for: $NAME"
done

echo ""
echo "Done. $count mailbox(es) prepared in $PASSDIR"
ls -la "$PASSDIR"/*.pass
