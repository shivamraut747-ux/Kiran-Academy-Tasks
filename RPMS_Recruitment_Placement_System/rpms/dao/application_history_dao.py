from rpms.util.db_connection import fetch_all, execute


class ApplicationHistoryDAO:
    """Reads and writes the application_history audit table."""

    def add(self, application_id, old_status, new_status, remarks, changed_by, con=None):
        """Insert one history row. Pass con to make it part of a transaction."""
        sql = """INSERT INTO application_history
                 (application_id, old_status, new_status, remarks, changed_by)
                 VALUES (%s,%s,%s,%s,%s)"""
        return execute(sql, (application_id, old_status, new_status, remarks, changed_by), con)

    def find_by_application(self, application_id):
        sql = """SELECT h.history_id, h.old_status, h.new_status, h.remarks,
                        u.full_name AS changed_by, h.changed_at
                 FROM application_history h
                 JOIN users u ON u.user_id = h.changed_by
                 WHERE h.application_id=%s
                 ORDER BY h.history_id"""
        return fetch_all(sql, (application_id,))
