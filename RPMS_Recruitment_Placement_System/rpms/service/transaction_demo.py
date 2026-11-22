from rpms.util.db_connection import transaction, fetch_one, execute


def rollback_demo():
    """
    Shows ROLLBACK to the examiner (Database PDF: 'one transaction rollback scenario').
    Step 1: change a candidate's college inside a transaction.
    Step 2: raise an error on purpose.
    Result: the database rolls back, so the college is exactly as before.
    Returns a list of text lines to print.
    """
    lines = []
    row = fetch_one("SELECT candidate_id, college FROM candidates ORDER BY candidate_id LIMIT 1")
    if not row:
        return ["No candidates found, demo skipped."]
    cid, original = row["candidate_id"], row["college"]
    lines.append(f"Before         : college = {original}")
    try:
        with transaction() as con:
            execute("UPDATE candidates SET college=%s WHERE candidate_id=%s", ("ROLLBACK DEMO", cid), con)
            inside = fetch_one("SELECT college FROM candidates WHERE candidate_id=%s", (cid,), con)
            lines.append(f"Inside (step 1): college = {inside['college']}   (not saved yet)")
            raise RuntimeError("Simulated failure at step 2")
    except RuntimeError as exc:
        lines.append(f"Error          : {exc}  -> ROLLBACK")
    after = fetch_one("SELECT college FROM candidates WHERE candidate_id=%s", (cid,))
    lines.append(f"After rollback : college = {after['college']}   (unchanged)")
    return lines
