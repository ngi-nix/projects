#!/usr/bin/env python3
"""Generate gh commands to create GitHub issues in ngi-nix/projects for each project.

Input file format (CSV):
  - First line is a header and is skipped
  - '|' as field separator
    - project name
    - semicolon separated list of fund names
    - semicolon separated subgrant URLs (https://nlnet.nl/project/<subgrant-name>)
  - Produced by group_subgrants.py.

Output:
  - One 'gh issue create' command per line, printed to stdout.
  - Subgrant URLs are appended to the issue body under a '### Subgrants' section.
"""

import sys
from pathlib import Path

REPO = "ngi-nix/projects"
LABELS = "User story,NGI Project"
PROJECT = "Nix@NGI"
TEMPLATE_BODY = """\
### Tasks

- [ ] {name}: Create a package recipe
- [ ] {name}: Create an application recipe
- [ ] {name}: Announce a packaged project
- [ ] {name}: Update NLnet project status

### Subgrants

{urls}
"""


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "projects.csv"
    lines = Path(path).read_text().splitlines()

    for line in lines[1:]:  # skip header
        line = line.strip()
        if not line:
            continue
        project, fund, urls_field = line.split("|", 2)
        fund_labels = ",".join(f"NGI0 {f}" for f in fund.split(";"))
        labels = f"{LABELS},{fund_labels}"
        urls = "\n".join(f"- {u}" for u in urls_field.split(";"))
        body = TEMPLATE_BODY.format(name=project, urls=urls)
        # Escape single quotes in body for shell safety
        body_escaped = body.replace("'", "'\\''")
        title = f"NGI Project: {project}"
        print(
            f"gh issue list --repo {REPO} --state all --search '{title}' --json title --jq '.[].title'"
            f" | grep -qixF '{title}'"
            f" || (echo 'Creating: {title}' && gh issue create"
            f" --repo {REPO}"
            f" --title '{title}'"
            f" --label '{labels}'"
            f" --project '{PROJECT}'"
            f" --body '{body_escaped}'"
            f" && echo 'Created: {title}')"
        )
        print()


if __name__ == "__main__":
    main()
