#! /usr/bin/env python3

"""
Check that each geographic value sits under a single parent, and report any that
do not.

The geographic fields nest: region contains country, country contains division,
division contains location. A value appearing under two different parents -- one
health zone recorded under two provinces -- means at least one of those records is
wrong, and splits any per-place count computed downstream.

Each pairing (country under region, division under country, location under
division) is checked independently. Records with an empty value or an empty parent
are skipped.

Every value with more than one parent is reported once with its total record
count, followed by one line per parent giving that parent's count and accessions,
e.g.

    Location Isiro (n=27) appears under 3 different division values
        division = Ituri   n=19   (PP_0085CLX, PP_0085CMV, ...)
        division = Haut-Uele   n=7   (PP_0084YES, ...)
        division = Haut-Uele   n=1   (PP_0084SZT)

Which parent is correct is not determined; the counts are there to judge by.

The report is written to --output; an empty file means every value has one parent.
"""

import argparse
import csv
import sys
from collections import defaultdict

# (child, parent, scope) in report order. `scope` is the grandparent field that
# disambiguates homonyms: two values of `child` with the same name are only
# compared when they share a scope. None means compare globally.
NESTED_FIELDS = [
    ("country", "region", None),
    ("division", "country", "region"),
    ("location", "division", "country"),
]


def read_metadata(path, id_column):
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = reader.fieldnames or []
        if id_column not in fieldnames:
            sys.exit(f"Metadata {path} has no {id_column!r} column")
        return list(reader), fieldnames


def read_exceptions(path):
    """Return {(resolution, value): {parent, ...}} of combinations known to be legitimate."""
    allowed = defaultdict(set)
    if not path:
        return allowed
    with open(path, encoding="utf-8", newline="") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 3:
                sys.exit(f"{path}: expected 3 tab-separated columns, got {line!r}")
            resolution, value, parent = (f.strip() for f in fields[:3])
            allowed[(resolution, value)].add(parent)
    return allowed


def find_split_values(rows, child, parent, scope, id_column, allowed):
    """Return {(scope_value, child_value): {parent_value: [id, ...]}} for children with >1 parent.

    A child is compared only against others sharing its scope, and a split whose
    parents are all listed in `allowed` is not returned.
    """
    seen = defaultdict(lambda: defaultdict(list))
    for row in rows:
        child_value = (row.get(child) or "").strip()
        parent_value = (row.get(parent) or "").strip()
        if not child_value or not parent_value:
            continue
        scope_value = (row.get(scope) or "").strip() if scope else ""
        seen[(scope_value, child_value)][parent_value].append(row.get(id_column, ""))
    return {
        key: parents
        for key, parents in seen.items()
        if len(parents) > 1 and not set(parents) <= allowed.get((child, key[1]), set())
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--metadata", required=True, help="Curated metadata TSV to check")
    parser.add_argument(
        "--id-column", default="accession", help="Metadata column identifying each record"
    )
    parser.add_argument(
        "--exceptions",
        help="TSV of resolution, value, parent naming homonyms that are legitimate",
    )
    parser.add_argument("--output", help="Report path (default: stdout only)")
    args = parser.parse_args()

    rows, fieldnames = read_metadata(args.metadata, args.id_column)
    allowed = read_exceptions(args.exceptions)

    lines = []
    n_values = 0
    for child, parent, scope in NESTED_FIELDS:
        missing = [f for f in (child, parent) if f not in fieldnames]
        if missing:
            print(
                f"Skipping {child!r} under {parent!r}: "
                f"{', '.join(repr(f) for f in missing)} not a column in {args.metadata}",
                file=sys.stderr,
            )
            continue
        scope_field = scope if scope in fieldnames else None
        split = find_split_values(rows, child, parent, scope_field, args.id_column, allowed)
        n_values += len(split)
        # Most-contested values first, then alphabetically, so the report is stable.
        for (scope_value, value), parents in sorted(
            split.items(), key=lambda kv: (-sum(len(v) for v in kv[1].values()), kv[0])
        ):
            total = sum(len(ids) for ids in parents.values())
            within = f" within {scope_field} {scope_value}" if scope_value else ""
            lines.append(
                f"{child.capitalize()} {value} (n={total}){within} "
                f"appears under {len(parents)} different {parent} values"
            )
            for parent_value, ids in sorted(parents.items(), key=lambda kv: (-len(kv[1]), kv[0])):
                lines.append(f"    {parent} = {parent_value}   n={len(ids)}   ({', '.join(ids)})")

    report = "\n".join(lines) + "\n" if lines else ""
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
    print(report, end="")

    print(
        f"{n_values} geographic value(s) appearing under more than one parent",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
