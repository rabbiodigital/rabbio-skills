#!/usr/bin/env python3
"""
test_connections.py

Test IMAP SSL connections for a set of mailboxes against a source and/or
destination server, using per-mailbox passfiles. Prints INBOX message counts.

Usage:
    test_connections.py \
        --src-server mail.example.com --src-port 993 \
        --dst-server imap.newhost.com --dst-port 993 \
        --passdir /tmp/imapsync_migration \
        --mailboxes sales@example.com:sales user@example.com:user

Each mailbox arg has the form  EMAIL:NAME  where NAME is the slug used in
the passfile names  (src_<NAME>.pass, dst_<NAME>.pass).

You can limit the test to one side only:
    --only src   (test only source)
    --only dst   (test only destination)

Exit code is 0 only when every requested check passes.
"""

import argparse
import imaplib
import sys
from pathlib import Path


def read_password(passfile: Path) -> str:
    # Passfiles are written with printf '%s' -- no trailing newline to strip,
    # but strip just in case the user edited them in an editor that added one.
    return passfile.read_text().rstrip("\r\n")


def test_login(server: str, port: int, email: str, passfile: Path, label: str) -> bool:
    try:
        password = read_password(passfile)
        conn = imaplib.IMAP4_SSL(server, port)
        conn.login(email, password)
        status, data = conn.select("INBOX", readonly=True)
        count = int(data[0]) if status == "OK" else "?"
        conn.logout()
        print(f"  OK    {label}: INBOX has {count} messages")
        return True
    except FileNotFoundError:
        print(f"  FAIL  {label}: passfile missing ({passfile})")
        return False
    except Exception as e:  # noqa: BLE001 - report anything the server throws
        msg = str(e).strip() or e.__class__.__name__
        print(f"  FAIL  {label}: {msg}")
        return False


def parse_mailboxes(items):
    parsed = []
    for item in items:
        if ":" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid mailbox spec '{item}'. Expected EMAIL:NAME"
            )
        email, name = item.split(":", 1)
        parsed.append((email.strip(), name.strip()))
    return parsed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src-server")
    ap.add_argument("--src-port", type=int, default=993)
    ap.add_argument("--dst-server")
    ap.add_argument("--dst-port", type=int, default=993)
    ap.add_argument("--passdir", required=True, help="Directory containing src_<NAME>.pass / dst_<NAME>.pass")
    ap.add_argument("--mailboxes", nargs="+", required=True, help="List of EMAIL:NAME pairs")
    ap.add_argument("--only", choices=("src", "dst", "both"), default="both")
    args = ap.parse_args()

    mailboxes = parse_mailboxes(args.mailboxes)
    passdir = Path(args.passdir)
    all_ok = True

    do_src = args.only in ("src", "both") and args.src_server
    do_dst = args.only in ("dst", "both") and args.dst_server

    if do_src:
        print("=" * 60)
        print(f"CONNECTION TEST – SOURCE SERVER ({args.src_server})")
        print("=" * 60)
        for email, name in mailboxes:
            pf = passdir / f"src_{name}.pass"
            ok = test_login(args.src_server, args.src_port, email, pf, email)
            all_ok = all_ok and ok
        print()

    if do_dst:
        print("=" * 60)
        print(f"CONNECTION TEST – DESTINATION SERVER ({args.dst_server})")
        print("=" * 60)
        for email, name in mailboxes:
            pf = passdir / f"dst_{name}.pass"
            ok = test_login(args.dst_server, args.dst_port, email, pf, email)
            all_ok = all_ok and ok
        print()

    if not do_src and not do_dst:
        print("Nothing to test: specify --src-server and/or --dst-server.", file=sys.stderr)
        return 2

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
