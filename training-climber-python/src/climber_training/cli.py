from __future__ import annotations

import argparse
import json
from pathlib import Path

from climber_training.rule_engine import exportar_ruleset, validate_rule_package


def main() -> int:
    parser = argparse.ArgumentParser(prog="climber-rules")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate"); validate.add_argument("path", type=Path)
    export = sub.add_parser("export"); export.add_argument("path", type=Path); export.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "validate":
        errors = validate_rule_package(args.path)
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        return int(bool(errors))
    exportar_ruleset(args.path, args.destination)
    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
