#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

python "$ROOT/scripts/cds_audit/cds_audit.py" --out /tmp/cds_cross_final.tsv

for mod in "$ROOT"/scripts/cds_audit/modules/*.py; do
  python "$mod"
  echo "---"
 done
