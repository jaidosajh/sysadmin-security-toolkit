# SysAdmin Security Toolkit

**Practical, read-only defensive automation for systems administrators and cybersecurity analysts.**

This repository contains reproducible utilities for authentication-event triage, file-integrity monitoring, Windows local account auditing, and Linux security posture checks. It is a public portfolio project built with **synthetic sample data**, not production customer information.

## Tools

| Utility | Platform | What it does |
| --- | --- | --- |
| `auth_log_triage.py` | Python 3.9+ | Flags repeated failed authentications by source IP and successes after failures for an account/IP within a rolling window |
| `file_integrity.py` | Python 3.9+ | Captures and verifies SHA-256 file manifests in explicitly selected directories |
| `Get-LocalSecurityAudit.ps1` | Windows PowerShell 5.1+ | Reads local accounts and the built-in Administrators group membership |
| `linux-security-audit.sh` | Linux / Bash | Displays local kernel, listening TCP sockets, and available firewall status |

## Quick start

No third-party Python dependencies are required. Run these commands **from the repository root**:

```bash
python scripts/python/auth_log_triage.py samples/auth_events.csv
python scripts/python/auth_log_triage.py samples/auth_events.csv --threshold 3 --output report.json
python -m unittest discover -s tests -v
```

Expected alert categories for the provided synthetic sample are `repeated_failures` and `success_after_failures`.

File integrity walkthrough (use a temporary test directory; keep your manifest outside that directory):

```bash
mkdir -p test-files
printf 'example\n' > test-files/example.txt
python scripts/python/file_integrity.py baseline test-files baseline.json
python scripts/python/file_integrity.py verify test-files baseline.json
```

Windows local account inventory (on an authorized Windows device):

```powershell
.\scripts\powershell\Get-LocalSecurityAudit.ps1 -OutputPath .\local-audit.json
```

Linux read-only posture summary:

```bash
bash scripts/bash/linux-security-audit.sh
```

## Interpreting results

- **Repeated failures** indicate an IP met or exceeded the selected threshold in a sliding window. This is a triage heuristic, **not proof of an attack**.
- **Success after failures** means an account/IP succeeded after one or more recent failures; investigate additional context before escalating.
- File integrity verification exits with status **0** for no changes and **1** when changes are found. Hash changes do not establish malicious intent.
- Windows and Linux utilities return **local inventory**, not a compliance certification or comprehensive security assessment.

## Responsible use

Run only against systems and datasets you own or are expressly authorized to assess. Never commit live logs, secrets, endpoint inventories, or client configurations. Reports can contain hostnames, usernames, and IP addresses; restrict storage and sharing. File integrity checks can be resource-intensive on large trees; symlinks are ignored.

## Project structure

```text
scripts/
  python/auth_log_triage.py
  python/file_integrity.py
  powershell/Get-LocalSecurityAudit.ps1
  bash/linux-security-audit.sh
samples/auth_events.csv
tests/
  test_auth_log_triage.py
  test_file_integrity.py
docs/ROADMAP.md
.github/workflows/python-tests.yml
```

## Roadmap

See [ROADMAP](docs/ROADMAP.md) for planned improvements.

## Author

**Jai Dosajh** · Cybersecurity Analyst / Systems Administrator · [GitHub](https://github.com/jaidosajh)

Licensed under MIT. These tools are educational references without warranty.
