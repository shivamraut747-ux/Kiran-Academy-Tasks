# Phase 5 - Reports and menu

New: sql/reports.sql (13 queries), rpms/app/report_menu.py, tests/test_phase5.py
Changed: rpms/service/report_service.py (all queries in a REPORTS dictionary; old method kept), rpms/app/main.py (Reports menu moved out).

Reports: Candidates by Technology, Open Jobs, Open Jobs by Company, Applications by Status, Recruitment Funnel,
Company-wise Placements, Technology-wise Placements, Recruiter Performance, Pending Interviews,
Offer-to-Joining Conversion, Open Job Aging, Placed Candidates, Unplaced Candidates.
The Reports menu builds itself from the REPORTS dictionary and writes each view to activity_log.txt.

Test: python -m unittest tests.test_phase5 -v ; in MySQL: SOURCE sql/reports.sql;
