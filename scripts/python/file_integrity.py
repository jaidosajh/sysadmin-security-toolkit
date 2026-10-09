#!/usr/bin/env python3
"""Create and compare SHA-256 file manifests for an explicitly selected directory."""
import argparse
import hashlib
import json
from pathlib import Path

def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()

def snapshot(root):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("target must be a directory")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        result[path.relative_to(root).as_posix()] = digest(path)
    return result

def compare(baseline, current):
    original, observed = set(baseline), set(current)
    return {"added": sorted(observed - original), "removed": sorted(original - observed),
            "changed": sorted(p for p in original & observed if baseline[p] != current[p])}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("baseline", help="Save a SHA-256 manifest")
    init.add_argument("directory", type=Path)
    init.add_argument("manifest", type=Path)
    check = commands.add_parser("verify", help="Compare a directory against a saved manifest")
    check.add_argument("directory", type=Path)
    check.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "baseline":
            if args.manifest.resolve().is_relative_to(args.directory.resolve()):
                raise ValueError("manifest must be outside the scanned directory")
            data = snapshot(args.directory)
            args.manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print(f"Created manifest for {len(data)} files")
        else:
            baseline = json.loads(args.manifest.read_text(encoding="utf-8"))
            if not isinstance(baseline, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in baseline.items()):
                raise ValueError("invalid manifest format")
            report = compare(baseline, snapshot(args.directory))
            print(json.dumps(report, indent=2))
            if any(report.values()):
                raise SystemExit(1)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
