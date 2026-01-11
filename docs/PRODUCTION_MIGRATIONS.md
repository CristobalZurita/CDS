# Production migration & deduplication runbook ✅

This runbook describes safe steps to detect and resolve duplicate `transaction_id` values in `payments` and to apply the Alembic migration that adds the UNIQUE index/constraint in production (Postgres).

IMPORTANT: Always take a backup / DB snapshot before performing changes in production.

## Quick checklist (high level)

- Verify you have a recent DB backup/snapshot and the required permissions (DDL + UPDATE).
- Confirm a maintenance window if your site must enforce strict rolling writes.
- Run the dedupe script in dry-run mode, inspect changes, then apply if satisfied.
- Run `alembic upgrade head` in production (migration `0004` is Postgres-friendly and creates an index concurrently).
- Verify the unique index is present and that duplicate inserts now fail.

## Step-by-step

1) Preflight checks

   - Confirm `DATABASE_URL` points to the intended environment (staging/production).
   - Verify you have a backup: take a snapshot or dump using your usual backup tooling.
   - Run a quick query to find duplicates:

     ```sql
     SELECT transaction_id, count(*) AS cnt
     FROM payments
     GROUP BY transaction_id
     HAVING count(*) > 1
     ORDER BY cnt DESC
     LIMIT 50;
     ```

2) Dry-run dedupe

   - From the repository root run:
     ```bash
     python scripts/dedupe_payments_transaction_ids.py --dry-run --database-url "$DATABASE_URL"
     ```
   - Inspect the output carefully: it will show which rows would be modified. No changes occur in dry-run.

3) Apply dedupe (if dry-run is satisfactory)

   - Execute in a maintenance window or when acceptable:
     ```bash
     python scripts/dedupe_payments_transaction_ids.py --apply --database-url "$DATABASE_URL"
     ```
   - The script appends the `id` to the `transaction_id` of duplicate rows to make them unique while keeping the original earliest/primary row intact.

4) Apply Alembic migrations

   - With dedup applied, run Alembic to add the unique index/constraint:
     ```bash
     alembic upgrade head
     ```
   - The migration `0004` creates a concurrent unique index in Postgres and is non-blocking.

5) Verification

   - Confirm duplicates are gone:
     ```sql
     SELECT transaction_id, count(*) FROM payments GROUP BY transaction_id HAVING count(*) > 1;
     ```
   - Attempt a duplicate insert (from a safe test) and verify it fails.

6) Rollback plan

   - If something goes wrong, restore from the snapshot/backup you created in step 1.

## Notes & caveats

- The application-level idempotency check will already return an existing payment when a `transaction_id` exists. The DB constraint is an additional safety net for production.
- If you expect extremely high parallel requests for the same `transaction_id`, consider an application-level locking mechanism (e.g., advisory locks) for critical flows.

---

If you want, I can also prepare a one-click command snippet or a small shell script that runs the dry-run and opens a PR checklist for operations teams to sign off before applying the `--apply` step.
