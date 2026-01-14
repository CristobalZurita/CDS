"""Utility to dedupe duplicate transaction_id values in payments table.

Usage:
    python scripts/dedupe_payments_transaction_ids.py --dry-run
    python scripts/dedupe_payments_transaction_ids.py --apply

This script is safe to run in production as a manual step: it will leave the earliest payment for each transaction_id intact and append the id to subsequent duplicates to make them unique.
"""

import argparse
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from sqlalchemy import text


def main(apply: bool = False):
    db = SessionLocal()
    try:
        # Find duplicate transaction_ids
        rows = db.execute(text("SELECT transaction_id, COUNT(*) AS cnt FROM payments WHERE transaction_id IS NOT NULL GROUP BY transaction_id HAVING COUNT(*) > 1")).fetchall()
        if not rows:
            print("No duplicates found.")
            return
        print(f"Found {len(rows)} duplicate transaction_id groups.")
        for r in rows:
            tx = r[0]
            print(f"Processing transaction_id={tx}")
            # Keep the row with the smallest id
            dup_rows = db.execute(text("SELECT id FROM payments WHERE transaction_id = :tx ORDER BY id"), {"tx": tx}).fetchall()
            ids = [d[0] for d in dup_rows]
            keeper = ids[0]
            to_update = ids[1:]
            print(f"  keeper={keeper}, to_update={to_update}")
            if apply:
                for uid in to_update:
                    new_val = f"{tx}_{uid}"
                    db.execute(text("UPDATE payments SET transaction_id = :new WHERE id = :id"), {"new": new_val, "id": uid})
                db.commit()
                print(f"  Updated {len(to_update)} rows.")
            else:
                print("  Dry run: no changes made.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply fixes")
    args = parser.parse_args()
    main(apply=args.apply)
