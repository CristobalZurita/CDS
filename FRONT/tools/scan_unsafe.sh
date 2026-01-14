#!/usr/bin/env bash
# Scan repo for unsafe JS patterns (eval, new Function, innerHTML)
set -euo pipefail

echo "Scanning for unsafe patterns (eval|new Function|innerHTML|document\.write)..."
if git grep -n --untracked --cached -E "\beval\(|new Function\(|innerHTML|document\.write\(|\beval\s|Function\("; then
  echo "\nERROR: Found potential unsafe patterns. Please review the grep output above and remove or audit before committing." >&2
  exit 1
else
  echo "No matches found."
fi

exit 0
