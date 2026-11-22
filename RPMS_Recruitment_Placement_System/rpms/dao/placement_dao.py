from rpms.util.db_connection import fetch_all, fetch_one, execute


class PlacementDAO:
    """placements table (+ the candidate's placement_status). Pass con to join a transaction."""

    def find_by_id(self, placement_id, con=None, lock=False):
        sql = """SELECT p.*, o.application_id FROM placements p
                 JOIN offers o ON o.offer_id = p.offer_id WHERE p.placement_id=%s"""
        if lock:
            sql += " FOR UPDATE"
        return fetch_one(sql, (placement_id,), con)

    def find_by_offer(self, offer_id, con=None):
        return fetch_one("SELECT * FROM placements WHERE offer_id=%s", (offer_id,), con)

    def insert(self, ctx, joining_status, actual_joining_date, con=None):
        """ctx = row from OfferDAO.context()"""
        sql = """INSERT INTO placements (candidate_id, company_id, job_id, offer_id, designation,
                 final_package_lpa, expected_joining_date, actual_joining_date, joining_status)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        return execute(sql, (ctx["candidate_id"], ctx["company_id"], ctx["job_id"], ctx["offer_id"],
                             ctx["designation"], ctx["offered_package_lpa"],
                             ctx["expected_joining_date"], actual_joining_date, joining_status), con)

    def update_joining(self, placement_id, joining_status, actual_joining_date, con=None):
        execute("UPDATE placements SET joining_status=%s, actual_joining_date=%s "
                "WHERE placement_id=%s", (joining_status, actual_joining_date, placement_id), con)

    def mark_candidate_placed(self, candidate_id, con=None):
        execute("UPDATE candidates SET placement_status='PLACED', updated_at=NOW() "
                "WHERE candidate_id=%s", (candidate_id,), con)

    def search(self, joining_status=None):
        sql = """SELECT p.placement_id, c.candidate_code, c.full_name, co.company_name,
                        p.designation, p.final_package_lpa, p.expected_joining_date,
                        p.actual_joining_date, p.joining_status, p.placement_status
                 FROM placements p
                 JOIN candidates c ON c.candidate_id = p.candidate_id
                 JOIN companies co ON co.company_id = p.company_id
                 WHERE 1=1"""
        params = []
        if joining_status:
            sql += " AND p.joining_status=%s"; params.append(joining_status)
        return fetch_all(sql + " ORDER BY p.placement_id DESC", tuple(params))
