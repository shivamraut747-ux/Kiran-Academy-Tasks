from rpms.util.db_connection import fetch_all, fetch_one, execute

OPEN_STATUSES = ("SCHEDULED", "RESCHEDULED")


class InterviewDAO:
    """interview_rounds + interview_feedback tables. Pass con to join a transaction."""

    def find_by_id(self, interview_id, con=None, lock=False):
        sql = "SELECT * FROM interview_rounds WHERE interview_id=%s"
        if lock:
            sql += " FOR UPDATE"
        return fetch_one(sql, (interview_id,), con)

    def max_round(self, application_id, con=None):
        row = fetch_one("SELECT COALESCE(MAX(round_number),0) AS n FROM interview_rounds "
                        "WHERE application_id=%s", (application_id,), con)
        return int(row["n"])

    def open_round_exists(self, application_id, con=None):
        row = fetch_one("SELECT 1 AS x FROM interview_rounds WHERE application_id=%s "
                        "AND status IN ('SCHEDULED','RESCHEDULED') LIMIT 1", (application_id,), con)
        return row is not None

    def insert(self, application_id, round_number, round_type, scheduled_date,
               scheduled_time, mode, interviewer, location, con=None):
        sql = """INSERT INTO interview_rounds (application_id, round_number, round_type,
                 scheduled_date, scheduled_time, mode, interviewer_name, meeting_or_location)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        return execute(sql, (application_id, round_number, round_type, scheduled_date,
                             scheduled_time, mode, interviewer, location), con)

    def reschedule(self, interview_id, scheduled_date, scheduled_time, con=None):
        execute("UPDATE interview_rounds SET scheduled_date=%s, scheduled_time=%s, "
                "status='RESCHEDULED' WHERE interview_id=%s",
                (scheduled_date, scheduled_time, interview_id), con)

    def set_status(self, interview_id, status, con=None):
        execute("UPDATE interview_rounds SET status=%s WHERE interview_id=%s",
                (status, interview_id), con)

    def feedback_exists(self, interview_id, con=None):
        return fetch_one("SELECT 1 AS x FROM interview_feedback WHERE interview_id=%s",
                         (interview_id,), con) is not None

    def insert_feedback(self, interview_id, technical, communication, problem_solving,
                        overall, recommendation, remarks, submitted_by, con=None):
        sql = """INSERT INTO interview_feedback (interview_id, technical_rating,
                 communication_rating, problem_solving_rating, overall_rating,
                 recommendation, remarks, submitted_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        return execute(sql, (interview_id, technical, communication, problem_solving,
                             overall, recommendation, remarks, submitted_by), con)

    def search(self, status=None, candidate_name=None, date_from=None, date_to=None, pending_only=False):
        sql = """SELECT i.interview_id, a.application_code, c.full_name, co.company_name,
                        i.round_number, i.round_type, i.scheduled_date, i.scheduled_time,
                        i.mode, i.interviewer_name, i.status
                 FROM interview_rounds i
                 JOIN applications a ON a.application_id = i.application_id
                 JOIN candidates c ON c.candidate_id = a.candidate_id
                 JOIN jobs j ON j.job_id = a.job_id
                 JOIN companies co ON co.company_id = j.company_id
                 WHERE 1=1"""
        params = []
        if pending_only:
            sql += " AND i.status IN ('SCHEDULED','RESCHEDULED')"
        if status:
            sql += " AND i.status=%s"; params.append(status)
        if candidate_name:
            sql += " AND c.full_name LIKE %s"; params.append(f"%{candidate_name}%")
        if date_from:
            sql += " AND i.scheduled_date >= %s"; params.append(date_from)
        if date_to:
            sql += " AND i.scheduled_date <= %s"; params.append(date_to)
        sql += " ORDER BY i.scheduled_date, i.scheduled_time"
        return fetch_all(sql, tuple(params))
