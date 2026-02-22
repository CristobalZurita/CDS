#!/usr/bin/env bash
set -euo pipefail

AXIOS_DIRECT_PATTERN="import\\s+axios\\s+from|axios\\.(get|post|put|patch|delete|create)"

echo "Checking direct axios usage in Vue components/views..."
vue_matches="$(rg -n -P "${AXIOS_DIRECT_PATTERN}" src/vue src/views --glob '*.vue' --glob '*.js' --glob '*.ts' || true)"
if [[ -n "${vue_matches}" ]]; then
  echo "Direct axios usage found in components/views:"
  echo "${vue_matches}"
  exit 1
fi

echo "Checking direct axios usage in composables (except useApi)..."
composable_matches="$(rg -n -P "${AXIOS_DIRECT_PATTERN}" src/composables --glob '*.js' --glob '*.ts' --glob '!useApi.js' --glob '!useApi.ts' || true)"
if [[ -n "${composable_matches}" ]]; then
  echo "Direct axios usage found in composables:"
  echo "${composable_matches}"
  exit 1
fi

echo "API layer compliance checks passed."
