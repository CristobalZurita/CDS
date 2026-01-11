#!/usr/bin/env python3
"""Simple environment validator for required production secrets.

Usage:
    python scripts/check_env.py [--env-file .env] [--strict]

If ENVIRONMENT=production (or --strict) the script ensures that SECRET_KEY and JWT_SECRET and JWT_REFRESH_SECRET are present.
"""
import os
import sys
from argparse import ArgumentParser

REQUIRED = ["SECRET_KEY", "JWT_SECRET", "JWT_REFRESH_SECRET"]


def load_dotenv(path):
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    p = ArgumentParser()
    p.add_argument("--env-file", default=".env", help="Path to .env file to load (optional)")
    p.add_argument("--strict", action="store_true", help="Treat as production and require secrets")
    args = p.parse_args()

    load_dotenv(args.env_file)

    env = os.environ.get("ENVIRONMENT", "development").lower()
    is_prod = args.strict or env == "production" or env == "prod"

    missing = [k for k in REQUIRED if not os.environ.get(k)]

    if is_prod:
        if missing:
            print("Missing required production environment variables:")
            for k in missing:
                print(f" - {k}")
            print("\nPlease set these in your hosting environment or in your .env file before starting the app.")
            sys.exit(2)
        else:
            print("All required production environment variables are present ✅")
            sys.exit(0)

    print(f"ENVIRONMENT={env}; not enforcing production secrets. Use --strict to enforce or set ENVIRONMENT=production.")
    if missing:
        print("Missing optional variables (only required in production):")
        for k in missing:
            print(f" - {k}")
    else:
        print("All known variables present.")


if __name__ == "__main__":
    main()
