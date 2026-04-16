---
name: imapsync-migration
description: Migrate IMAP email mailboxes between hosting providers using imapsync, with parallel execution, connection testing via Python imaplib, passfile handling for passwords with special characters, and post-MX-change incremental resync via source IP. Use ONLY when the user explicitly invokes this skill by name or explicitly asks for "imapsync", "IMAP migration", "email mailbox migration via imapsync", or a similar direct request. Do not trigger on generic "email" or "hosting" tasks.
---

# imapsync Email Migration

Universal workflow for migrating IMAP mailboxes between any two hosting providers using `imapsync`. Handles multiple mailboxes in parallel, passwords with special characters, and the tricky post-MX-change final resync.

## Language adaptation

The user may work in any language. **Mirror the user's language** in all chat responses, log summaries, and status tables. Keep config file comments and script output in English (they are technical). If the user writes in Slovak, respond in Slovak; if English, English; etc. Default to English only if the user's language is unclear.

## Prerequisites

- `imapsync` installed (`brew install imapsync` on macOS)
- Python 3 with `imaplib` (stdlib, always available)
- Shell with parallel backgrounding (`&`)

## Workflow overview

```
Task Progress:
- [ ] Step 1: Generate config template and have the user fill it in
- [ ] Step 2: Create passfiles for each mailbox
- [ ] Step 3: Test IMAP connections on source and destination
- [ ] Step 4: Run imapsync in parallel for all mailboxes
- [ ] Step 5: Monitor progress until all finish
- [ ] Step 6 (after MX change): Final incremental resync via source IP
- [ ] Step 7: Cleanup (remove passfiles and config)
```

Track this list explicitly and update as each step completes.

## Step 1: Generate config template

Create a config file the user can fill in. Use `/tmp/imapsync_migration_config.txt` so it is local and temporary.

```bash
cat << 'EOF' > /tmp/imapsync_migration_config.txt
# === EMAIL MIGRATION – CONFIGURATION ===

# SOURCE SERVER (old hosting)
SRC_SERVER=
SRC_PORT=993
SRC_IP=
# (Fill IP if known – required after MX change, when hostname stops resolving to old server)

# DESTINATION SERVER (new hosting)
DST_SERVER=
DST_PORT=993

# MAILBOXES (email | source password | destination password)
# Add/remove rows as needed:
BOX1_EMAIL=
BOX1_SRC_PASS=
BOX1_DST_PASS=

BOX2_EMAIL=
BOX2_SRC_PASS=
BOX2_DST_PASS=

BOX3_EMAIL=
BOX3_SRC_PASS=
BOX3_DST_PASS=

EOF
echo "Template created: /tmp/imapsync_migration_config.txt"
```

Ask the user to fill it in, then read the filled file to extract credentials.

## Step 2: Create passfiles

**Why passfiles, not `--password1/--password2`?** Passwords often contain shell-unsafe characters (`$`, `!`, `<`, `>`, `;`, `{`, `}`, `%`). Passfiles avoid all quoting issues.

Use the bundled helper to generate passfiles from an in-memory list, or write them directly. Each passfile contains **only the password, no trailing newline**, with `chmod 600`.

```bash
mkdir -p /tmp/imapsync_migration/logs

# For each mailbox (NAME = short slug derived from the local-part):
printf '%s' 'THE_SOURCE_PASSWORD' > /tmp/imapsync_migration/src_NAME.pass
printf '%s' 'THE_DEST_PASSWORD'   > /tmp/imapsync_migration/dst_NAME.pass

chmod 600 /tmp/imapsync_migration/*.pass
```

**Important:**
- Use `printf '%s'` (not `echo`) so there is no trailing newline.
- If source and destination passwords differ for a mailbox, write them separately. Flag this to the user when you see it in the config.
- Derive `NAME` from the local-part (before `@`). E.g. `sales@domain.com` → `sales`, `milan.cupra@x.sk` → `milan.cupra`.

See [scripts/create_passfiles.sh](scripts/create_passfiles.sh) for a reusable helper.

## Step 3: Test connections

Run a Python IMAP login test on both sides for every mailbox **before** starting `imapsync`. Report a table showing status and INBOX message count. This catches wrong passwords, wrong hostnames, and server issues early.

Use [scripts/test_connections.py](scripts/test_connections.py):

```bash
python3 scripts/test_connections.py \
  --src-server mail.example.com --src-port 993 \
  --dst-server imap.newhost.com --dst-port 993 \
  --passdir /tmp/imapsync_migration \
  --mailboxes sales@example.com:sales user@example.com:user
```

The script prints:

```
============================================================
CONNECTION TEST – SOURCE SERVER (mail.example.com)
============================================================
  OK    sales@example.com: INBOX has 463 messages
  FAIL  user@example.com:  AUTHENTICATIONFAILED
...
```

If any mailbox fails:
1. Stop and report which mailboxes failed.
2. Ask the user to verify/update the password on the relevant side.
3. Re-run only the failed checks (the script supports specifying a subset).

**Do not proceed to imapsync until all mailboxes pass on both sides.**

## Step 4: Run imapsync in parallel

Launch one `imapsync` process per mailbox in the background. Log stdout per mailbox to a separate file.

```bash
for box in \
  "sales@example.com:sales" \
  "user@example.com:user"
do
  EMAIL="${box%%:*}"
  NAME="${box##*:}"

  imapsync \
    --host1 mail.example.com --port1 993 --ssl1 \
    --user1 "$EMAIL" --passfile1 "/tmp/imapsync_migration/src_${NAME}.pass" \
    --host2 imap.newhost.com --port2 993 --ssl2 \
    --user2 "$EMAIL" --passfile2 "/tmp/imapsync_migration/dst_${NAME}.pass" \
    --no-modulesversion --exclude "Trash" --errorsmax 100 \
    --logdir /tmp/imapsync_migration/logs \
    > "/tmp/imapsync_migration/logs/${NAME}_stdout.log" 2>&1 &

  echo "Started: $EMAIL (PID: $!)"
done
```

**Flag rationale:**
- `--ssl1 / --ssl2` – IMAPS on port 993
- `--passfile1 / --passfile2` – avoid shell quoting issues
- `--no-modulesversion` – skip module version check, faster startup
- `--exclude "Trash"` – the Trash folder often fails with `SERVERBUG Internal error` on Websupport-style servers
- `--errorsmax 100` – tolerate more than the default 50 errors before aborting (useful on large mailboxes)
- `--logdir` – imapsync writes its own detailed log per run here

**imapsync is incremental** – safe to re-run. It only transfers new messages.

## Step 5: Monitor progress

Poll in a loop. For each mailbox, check if the PID is still running and show the last log lines.

```bash
for NAME in sales user; do
  echo "--- ${NAME}@ ---"
  if pgrep -f "user1.*${NAME}@" > /dev/null 2>&1; then
    echo "RUNNING"
  else
    EXIT=$(grep -o 'return value [0-9]*' /tmp/imapsync_migration/logs/${NAME}_stdout.log | tail -1)
    ERRORS=$(grep -o 'Detected [0-9]* errors' /tmp/imapsync_migration/logs/${NAME}_stdout.log | tail -1)
    echo "DONE | $EXIT | $ERRORS"
  fi
  tail -3 /tmp/imapsync_migration/logs/${NAME}_stdout.log
  echo ""
done
```

Poll every 30–60 seconds while any process is running. Present a compact status table after each poll.

A clean finish looks like: `Exiting with return value 0 (EX_OK)` and `Detected 0 errors`.

## Step 6: Final resync after MX change

**Why a second pass?** Between the first sync and the MX DNS change, new mail may have arrived at the old server. After MX switches, the hostname (e.g. `mail.example.com`) often points to the new server (or stops resolving to the old one), so the old mailbox becomes unreachable by hostname.

**Solution**: after MX change, resync using the **direct IP address** of the old server as `--host1`.

```bash
imapsync \
  --host1 192.0.2.10 --port1 993 --ssl1 \
  --user1 "sales@example.com" --passfile1 /tmp/imapsync_migration/src_sales.pass \
  --host2 imap.newhost.com --port2 993 --ssl2 \
  --user2 "sales@example.com" --passfile2 /tmp/imapsync_migration/dst_sales.pass \
  --no-modulesversion --exclude "Trash" --errorsmax 100 \
  --logdir /tmp/imapsync_migration/logs
```

Run the same parallel loop as Step 4 but with `--host1 <SRC_IP>`. Log files should use a different suffix (e.g. `${NAME}_resync_stdout.log`) so initial logs are preserved.

If the source server uses a certificate tied to the hostname and strict SNI/cert validation kicks in, imapsync may fail TLS verification. If this happens, add `--sslargs1 SSL_verify_mode=0` to disable source-side cert verification (only acceptable because the IP is the same server we already synced from).

A successful resync shows: `Messages transferred: 0` (nothing new) or a small delta count.

## Step 7: Cleanup

Only after the user confirms everything works on the new host:

```bash
rm -rf /tmp/imapsync_migration /tmp/imapsync_migration_config.txt
```

This removes passfiles (containing plaintext passwords), imapsync logs, and the config template.

## Known issues and fixes

| Problem | Fix |
|---|---|
| `SERVERBUG Internal error` on Trash folder (Websupport, some Dovecot setups) | Add `--exclude "Trash"` |
| Password with `$`, `!`, `<`, `>`, `;` breaking CLI | Use `--passfile1/--passfile2` with `printf '%s'` (no newline) |
| `AUTHENTICATIONFAILED` during test | Wrong password, or server requires app-specific password, or mailbox not yet created on destination |
| Hostname stops resolving to old server after MX change | Use direct IP in `--host1` |
| `--errorsmax 50` hit on large, messy mailboxes | Raise with `--errorsmax 100` (or higher) |
| Hanging TLS negotiation | Check firewall, try `--tls1 --notls1` combos, or `--debugssl 1` |
| Folder name mismatch (`INBOX.Sent` vs `Sent`) | imapsync auto-maps common prefixes; if it fails, use `--regextrans2 's,INBOX\.,,'` |

## Safety notes

- Passfiles contain plaintext passwords. Always `chmod 600` and clean up at the end.
- Never commit `/tmp/imapsync_migration/` or any config file with real credentials.
- imapsync is **read-only on the source** by default — it does not delete source messages unless `--delete1` is explicitly passed. Never pass `--delete1` unless the user explicitly requests it.
- Always run the connection test (Step 3) before the migration. It takes seconds and prevents wasted time.

## Reporting format

After each major step, show the user a compact status table like:

```
| Mailbox              | Source INBOX | Dest INBOX | Status     |
|----------------------|--------------|------------|------------|
| sales@example.com    | 463          | 0          | ready      |
| user@example.com     | 1685         | 0          | ready      |
```

For migration progress:

```
| Mailbox              | State        | Progress       | Errors |
|----------------------|--------------|----------------|--------|
| sales@example.com    | running      | 420/463 msgs   | 0      |
| user@example.com     | done         | 1685/1685 msgs | 0      |
```

Keep updates concise. Do not dump full imapsync logs into chat — summarise.
