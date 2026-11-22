from rpms.util.db_connection import fetch_all, fetch_one, execute


class OfferDAO:
    """offers table. Pass con to join a transaction."""

    def next_code(self, year, con=None):
        row = fetch_one("""SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(offer_code,'-',-1) AS UNSIGNED)),0) AS n
                           FROM offers WHERE offer_code LIKE %s""", (f"OFF-{year}-%",), con)
        return f"OFF-{year}-{int(row['n']) + 1:03d}"

    def find_by_id(self, offer_id, con=None, lock=False):
        sql = "SELECT * FROM offers WHERE offer_id=%s"
        if lock:
            sql += " FOR UPDATE"
        return fetch_one(sql, (offer_id,), con)

    def find_by_application(self, application_id, con=None):
        return fetch_one("SELECT * FROM offers WHERE application_id=%s", (application_id,), con)

    def context(self, offer_id, con=None):
        """Offer + the ids needed to create a placement (candidate, job, company)."""
        return fetch_one("""SELECT o.*, a.candidate_id, a.job_id, j.company_id
                            FROM offers o
                            JOIN applications a ON a.application_id = o.application_id
                            JOIN jobs j ON j.job_id = a.job_id
                            WHERE o.offer_id=%s""", (offer_id,), con)

    def insert(self, code, application_id, designation, package, offer_date,
               joining_date, remarks, con=None):
        sql = """INSERT INTO offers (offer_code, application_id, designation,
                 offered_package_lpa, offer_date, expected_joining_date, remarks)
                 VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        return execute(sql, (code, application_id, designation, package, offer_date,
                             joining_date, remarks), con)

    def set_status(self, offer_id, status, con=None):
        execute("UPDATE offers SET offer_status=%s WHERE offer_id=%s", (status, offer_id), con)

    def search(self, status=None):
        sql = """SELECT o.offer_id, o.offer_code, a.application_code, c.full_name, co.company_name,
                        o.designation, o.offered_package_lpa, o.offer_date,
                        o.expected_joining_date, o.offer_status
                 FROM offers o
                 JOIN applications a ON a.application_id = o.application_id
                 JOIN candidates c ON c.candidate_id = a.candidate_id
                 JOIN jobs j ON j.job_id = a.job_id
                 JOIN companies co ON co.company_id = j.company_id
                 WHERE 1=1"""
        params = []
        if status:
            sql += " AND o.offer_status=%s"; params.append(status)
        return fetch_all(sql + " ORDER BY o.offer_id DESC", tuple(params))
