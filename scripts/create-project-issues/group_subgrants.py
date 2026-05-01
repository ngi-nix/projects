#!/usr/bin/env python3
"""Group subgrants by project name and output as CSV.

Input file format:
  - CSV with ',' as separator, first line is a header and is skipped.
  - First column: subgrant name, must start with the project name, optionally
    followed by a hyphen and a variant suffix (e.g. "Kaidan", "Kaidan-Auth").
  - Second column: fund field, first word is the fund name
    (e.g. "Entrust", "Review", "Core", "Commons").

Output format (stdout):
  - CSV with '|' as field separator and ';' as subgrant/fund separator.
  - Header: project|fund|subgrants
  - Each row: <project-name>|<fund1>;<fund2>|<url1>;<url2>,...
    where URLs are https://nlnet.nl/project/<subgrant-name>.
  - All unique funds across subgrants in a group are included.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path


def load_names(path: str) -> list[tuple[str, str]]:
    """Return list of (subgrant_name, fund) tuples, skipping the header."""
    entries = []
    lines = Path(path).read_text().splitlines()
    for line in lines[1:]:  # skip header
        line = line.strip().lstrip("\ufeff")
        if not line:
            continue
        name, _, fund_field = line.partition(",")
        fund = fund_field.strip().split()[0] if fund_field.strip() else ""
        entries.append((name.strip(), fund))
    return entries


def tokenize(name: str) -> list[str]:
    return [t for t in re.split(r"[-_.\s/]+", name) if t]



def first_token(name: str) -> str:
    return tokenize(name)[0].lower()


def group_subgrants(entries: list[tuple[str, str]]) -> dict[str, tuple[str, list[str]]]:
    """Return {canonical_name: (fund, [other_subgrant_names])} grouped by first token."""
    token_to_entries: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for name, fund in entries:
        token_to_entries[first_token(name)].append((name, fund))

    result: dict[str, tuple[str, list[str]]] = {}
    for tok, members in token_to_entries.items():
        if len(members) < 2:
            continue
        names = [m[0] for m in members]
        # Canonical name: exact case-insensitive match to token, else shortest
        canonical = next((n for n in names if n.lower() == tok), None)
        if canonical is None:
            canonical = sorted(names, key=len)[0]
        # Collect all unique funds across all subgrants in the group
        seen: set[str] = set()
        funds = ";".join(f for _, f in members if f and not (f in seen or seen.add(f)))
        others = sorted((n for n in names if n != canonical), key=str.lower)
        result[canonical] = (funds, others)

    return dict(sorted(result.items(), key=lambda x: x[0].lower()))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "subgrants.csv"
    entries = load_names(path)
    groups = group_subgrants(entries)

    grouped_names = set(groups.keys()) | {sg for _, sgs in groups.values() for sg in sgs}
    singletons = sorted(((n, f) for n, f in entries if n not in grouped_names), key=lambda x: x[0].lower())

    def url(name: str) -> str:
        return f"https://nlnet.nl/project/{name}"

    rows = [(p, fund, [p] + sgs) for p, (fund, sgs) in groups.items()]
    rows += [(n, f, [n]) for n, f in singletons]
    rows.sort(key=lambda x: x[0].lower())

    print("project|fund|subgrants")
    for project, fund, subgrants in rows:
        print(f"{project}|{fund}|{';'.join(url(s) for s in subgrants)}")


if __name__ == "__main__":
    main()
