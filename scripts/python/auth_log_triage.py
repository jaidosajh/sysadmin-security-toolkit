#!/usr/bin/env python3
"""Analyze authorized or synthetic CSV authentication events. No network access."""
import argparse
import csv
import ipaddress
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED = {"timestamp", "username", "source_ip", "event", "outcome"}

def load_events(path: Path):
    events = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError(f"CSV requires columns: {', '.join(sorted(REQUIRED))}")
        for line, row in enumerate(reader, start=2):
            try:
                timestamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError("timestamp must have a timezone")
                source_ip = str(ipaddress.ip_address(row["source_ip"].strip()))
                outcome = row["outcome"].strip().lower()
                if outcome not in {"failure", "success"}:
                    raise ValueError("outcome must be success or failure")
                username = row["username"].strip()
                if not username:
                    raise ValueError("username is empty")
                events.append({"timestamp": timestamp.astimezone(timezone.utc),
                               "username": username, "source_ip": source_ip,
                               "event": row["event"].strip(), "outcome": outcome})
            except (ValueError, KeyError, AttributeError) as exc:
                raise ValueError(f"Invalid CSV row {line}: {exc}") from exc
    return sorted(events, key=lambda e: e["timestamp"])

def analyze(events, threshold=5, window_minutes=10):
    """Detect IP failure bursts and successful authentication following failures."""
    if threshold < 1 or window_minutes < 1:
        raise ValueError("threshold and window_minutes must be >= 1")
    window = timedelta(minutes=window_minutes)
    by_ip = defaultdict(list)
    by_identity = defaultdict(list)
    burst_reported = set()
    alerts = []
    for event in events:
        now = event["timestamp"]
        ip = event["source_ip"]
        key = (event["username"], ip)
        by_ip[ip] = [t for t in by_ip[ip] if now - t <= window]
        by_identity[key] = [t for t in by_identity[key] if now - t <= window]
        if event["outcome"] == "failure":
            by_ip[ip].append(now)
            by_identity[key].append(now)
            if len(by_ip[ip]) >= threshold and ip not in burst_reported:
                alerts.append({"type": "repeated_failures", "source_ip": ip,
                               "count": len(by_ip[ip]), "timestamp": now.isoformat(),
                               "severity": "medium"})
                burst_reported.add(ip)
        elif by_identity[key]:
            alerts.append({"type": "success_after_failures", "source_ip": ip,
                           "username": event["username"],
                           "prior_failures": len(by_identity[key]),
                           "timestamp": now.isoformat(), "severity": "high"})
            by_identity[key].clear()
        if len(by_ip[ip]) < threshold:
            burst_reported.discard(ip)
    return {"events_analyzed": len(events), "alerts": alerts, "alert_count": len(alerts)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--threshold", type=int, default=5)
    parser.add_argument("--window-minutes", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = analyze(load_events(args.csv_file), args.threshold, args.window_minutes)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    report = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"Wrote report to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
