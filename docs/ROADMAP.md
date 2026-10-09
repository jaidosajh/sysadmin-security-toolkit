# Project roadmap

The first release is intentionally small and independently testable.

## Possible follow-ups

- Add per-account failure thresholds, deduplication, and alert suppression policy.
- Support Windows Event XML converted into a normalized CSV, with documented event-ID mapping.
- Add JSON schema validation and a machine-readable export specification.
- Add Pester tests for Windows PowerShell and ShellCheck for Bash.
- Add optional verbose/evidence-safe reporting and alert disposition notes.
- Add sanitized diagrams and screenshots of a small authorized lab.

## Scope limitations

The log tool assumes normalized CSV, not raw Windows event logs or vendor logs. Thresholds are heuristics and may generate false positives. The local inventory scripts have not been validated across all supported Windows/Linux editions. Review and test locally before operational use.
