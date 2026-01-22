# Security guidance for local development

This project serves local content (API at `http://127.0.0.1:8000`) and a frontend. Treat all responses as untrusted input unless you control the source.

Quick protections we added:

- **Content Security Policy (CSP)**: `index.html` includes a CSP restricting script/style sources and only allowing fonts.googleapis.com and the local API in dev.
- **Scan script**: `tools/scan_unsafe.sh` looks for dangerous JS patterns (`eval`, `new Function`, `innerHTML`, `document.write`) and exits non-zero if found.

Developer rules:

- **Never** pipe `curl` output directly into a shell. E.g. avoid `curl ... | sh` or `curl ... | bash`. Inspect responses first.
- Use `jq` or `python -c 'import sys, json; print(json.load(sys.stdin))'` to safely parse JSON.
- When reviewing code that executes dynamic JS (e.g., `new Function(...)`), **require** a security justification and a unit test.
- Run `tools/scan_unsafe.sh` before committing; consider adding to CI or pre-commit hooks.

If you want, I can add a `pre-commit` configuration to run this scan automatically.

CI / tests:

- There is a pytest `backend/tests/test_security_scan.py` that runs `tools/scan_unsafe.sh` as part of test suite. Add this to CI to prevent unsafe patterns from being merged.
