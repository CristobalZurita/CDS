#!/usr/bin/env bash
set -euo pipefail

INLINE_PATTERN=":style\\s*=|v-bind:style\\s*=|(?<![-\\\\w])style\\s*=\\s*[\\\"']"
BACKEND_INLINE_PATTERN=":style\\s*=|v-bind:style\\s*=|(?<![-\\\\w])style\\s*=\\s*[\\\"']"
DOM_STYLE_MUTATION_PATTERN='\\.style\\.'
NON_SCSS_STYLE_PATTERN='<style(?![^>]*lang="scss")[^>]*>'

echo "Checking inline style usage in app source..."
inline_matches="$(rg -n -P --glob '!node_modules/**' --glob '!dist/**' "${INLINE_PATTERN}" src index.html || true)"
if [[ -n "${inline_matches}" ]]; then
  echo "Inline styles found:"
  echo "${inline_matches}"
  exit 1
fi

echo "Checking direct DOM style mutations in app source..."
dom_style_matches="$(rg -n --glob '!node_modules/**' --glob '!dist/**' "${DOM_STYLE_MUTATION_PATTERN}" src || true)"
if [[ -n "${dom_style_matches}" ]]; then
  echo "Direct DOM style mutations found:"
  echo "${dom_style_matches}"
  exit 1
fi

echo "Checking inline style usage in backend app code..."
backend_inline_matches="$(rg -n -P --glob '!backend/.venv/**' "${BACKEND_INLINE_PATTERN}" backend/app || true)"
if [[ -n "${backend_inline_matches}" ]]; then
  echo "Inline styles found in backend:"
  echo "${backend_inline_matches}"
  exit 1
fi

echo "Checking Vue style blocks use lang=\"scss\"..."
non_scss_matches="$(rg -n -P "${NON_SCSS_STYLE_PATTERN}" src --glob '*.vue' || true)"
if [[ -n "${non_scss_matches}" ]]; then
  echo "Vue style blocks without lang=\"scss\" found:"
  echo "${non_scss_matches}"
  exit 1
fi

echo "Style compliance checks passed."
