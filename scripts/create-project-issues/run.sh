#!/usr/bin/env -S nix shell nixpkgs#python3 -c bash
# Generate shell script containing commands to create issues from subgrants CSV
# file exported from Notion.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e -n "\nCreating projects.csv file ... "
python3 "$SCRIPT_DIR/group_subgrants.py" "$SCRIPT_DIR/subgrants.csv" > "$SCRIPT_DIR/projects.csv"
echo "Done."

echo -e -n "\nCreating create_issues.bash file ... "
python3 "$SCRIPT_DIR/create_issues.py" "$SCRIPT_DIR/projects.csv" > "$SCRIPT_DIR/create_issues.bash"
echo "Done."

echo -e "\nNow, run 'bash create_issues.bash' to create issues."
