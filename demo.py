"""Run a small synthetic example; try --exclude retry-change or any evidence ID."""

import argparse
import json
from pathlib import Path

from engine import rank, validate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()
    case = json.loads((Path(__file__).parent / "sample_case.json").read_text())
    hypotheses, invalid = validate(case["hypotheses"], case["evidence"], case["documents"])
    print(json.dumps({"synthetic": True, "invalid_citation_ids_removed": invalid,
                      "baseline": rank(hypotheses, case["evidence"]),
                      "after_exclusion": rank(hypotheses, case["evidence"], set(args.exclude))}, indent=2))


if __name__ == "__main__":
    main()
