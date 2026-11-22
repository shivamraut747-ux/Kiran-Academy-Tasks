-- =========================================================
-- reports.sql  |  Recruitment & Placement Management System
-- Run after rpms_full_setup.sql:  USE recruitment_portal;
-- Same queries as rpms/service/report_service.py
-- =========================================================

USE recruitment_portal;

-- 1. Candidates by Technology
SELECT COALESCE(primary_technology, 'Not set') AS technology, COUNT(*) AS total_candidates
FROM candidates
GROUP BY primary_technology
ORDER BY total_candidates DESC;

-- 2. Open Jobs
SELECT j.job_code, c.company_name, j.job_title, j.location, j.openings,
       j.application_deadline
FROM jobs j
JOIN companies c ON c.company_id = j.company_id
WHERE j.status = 'OPEN'
ORDER BY j.application_deadline;

-- 3. Open Jobs by Company
SELECT c.company_name, COUNT(j.job_id) AS open_jobs, SUM(j.openings) AS total_openings
FROM jobs j
JOIN companies c ON c.company_id = j.company_id
WHERE j.status = 'OPEN'
GROUP BY c.company_id, c.company_name
ORDER BY open_jobs DESC;

-- 4. Applications by Status
SELECT application_status, COUNT(*) AS total
FROM applications
GROUP BY application_status
ORDER BY total DESC;

-- 5. Recruitment Funnel (applications that reached each stage)
SELECT s.stage, COUNT(DISTINCT h.application_id) AS applications
FROM (SELECT 1 AS ord, 'APPLIED' AS stage
      UNION ALL SELECT 2, 'SHORTLISTED'
      UNION ALL SELECT 3, 'INTERVIEW_SCHEDULED'
      UNION ALL SELECT 4, 'INTERVIEWED'
      UNION ALL SELECT 5, 'SELECTED'
      UNION ALL SELECT 6, 'OFFERED'
      UNION ALL SELECT 7, 'JOINED') s
LEFT JOIN application_history h ON h.new_status = s.stage
GROUP BY s.ord, s.stage
ORDER BY s.ord;

-- 6. Company-wise Placements (JOINED)
SELECT c.company_name, COUNT(p.placement_id) AS placed_count
FROM placements p
JOIN companies c ON c.company_id = p.company_id
WHERE p.joining_status = 'JOINED'
GROUP BY c.company_id, c.company_name
ORDER BY placed_count DESC;

-- 7. Technology-wise Placements (JOINED)
SELECT COALESCE(cd.primary_technology, 'Not set') AS technology,
       COUNT(p.placement_id) AS placed_count
FROM placements p
JOIN candidates cd ON cd.candidate_id = p.candidate_id
WHERE p.joining_status = 'JOINED'
GROUP BY cd.primary_technology
ORDER BY placed_count DESC;

-- 8. Recruiter Performance
SELECT COALESCE(u.full_name, 'Unassigned') AS recruiter,
       COUNT(*) AS applications,
       SUM(a.application_status = 'SHORTLISTED') AS shortlisted,
       SUM(a.application_status IN ('SELECTED','OFFERED','JOINED')) AS selected_or_beyond,
       SUM(a.application_status = 'JOINED') AS joined,
       SUM(a.application_status = 'REJECTED') AS rejected
FROM applications a
LEFT JOIN users u ON u.user_id = a.assigned_recruiter_id
GROUP BY a.assigned_recruiter_id, u.full_name
ORDER BY applications DESC;

-- 9. Pending Interviews
SELECT i.interview_id, c.full_name AS candidate, co.company_name, i.round_type,
       i.scheduled_date, i.scheduled_time, i.mode, i.status
FROM interview_rounds i
JOIN applications a ON a.application_id = i.application_id
JOIN candidates c ON c.candidate_id = a.candidate_id
JOIN jobs j ON j.job_id = a.job_id
JOIN companies co ON co.company_id = j.company_id
WHERE i.status IN ('SCHEDULED','RESCHEDULED')
ORDER BY i.scheduled_date, i.scheduled_time;

-- 10. Offer-to-Joining Conversion
SELECT t.total_offers, j.joined, ROUND(j.joined * 100 / NULLIF(t.total_offers, 0), 1) AS conversion_percent
FROM (SELECT COUNT(*) AS total_offers FROM offers) t,
     (SELECT COUNT(*) AS joined FROM placements WHERE joining_status = 'JOINED') j;

-- 11. Open Job Aging
SELECT j.job_code, c.company_name, j.job_title, j.posted_date,
       DATEDIFF(CURDATE(), j.posted_date) AS days_open
FROM jobs j
JOIN companies c ON c.company_id = j.company_id
WHERE j.status = 'OPEN'
ORDER BY days_open DESC;

-- 12. Placed Candidates
SELECT cd.candidate_code, cd.full_name, co.company_name, p.designation,
       p.final_package_lpa, p.actual_joining_date
FROM placements p
JOIN candidates cd ON cd.candidate_id = p.candidate_id
JOIN companies co ON co.company_id = p.company_id
WHERE p.joining_status = 'JOINED'
ORDER BY p.actual_joining_date;

-- 13. Unplaced Candidates
SELECT candidate_code, full_name, primary_technology, qualification, passing_year,
       percentage, profile_status
FROM candidates
WHERE placement_status = 'NOT_PLACED'
ORDER BY candidate_code;
