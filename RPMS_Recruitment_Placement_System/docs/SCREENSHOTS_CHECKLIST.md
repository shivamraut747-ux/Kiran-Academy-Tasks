# Screenshots Checklist

Save images in `docs/screenshots/` named as shown. Tick when done.

## Console (take with real MySQL running)
- [x] 01-login-success.png
- [x] 02-main-menu.png
- [x] 03-candidate-add.png
- [x] 04-candidate-duplicate-blocked.png
- [x] 05-candidate-search.png
- [x] 06-company-list.png
- [x] 07-job-create-with-skills.png
- [x] 08-apply-success.png
- [x] 09-duplicate-application-blocked.png
- [x] 10-invalid-transition-blocked.png
- [x] 11-application-history.png
- [x] 12-interview-schedule.png
- [x] 13-interview-feedback.png
- [x] 14-offer-create.png
- [x] 15-placement-joined.png
- [x] 16-rollback-demo.png
- [x] 17-reports-menu.png
- [x] 18-report-recruitment-funnel.png
- [x] 19-report-company-wise-placements.png
- [x] 20-activity-log-file.png

## Tests and database
- [x] 21-unittest-all-pass.png (`python -m unittest discover -s tests -v`)
- [x] 22-mysql-tables.png (`SHOW TABLES;` – 17 tables)
- [x] 23-application-history-rows.png (`SELECT * FROM application_history;`)
- [x] 24-reports-sql-output.png (`SOURCE sql/reports.sql;`)
- [x] 25-er-diagram.png (from `docs/er_diagram.png`)

## HTML pages (already in `recruitment-placement-ui/screenshots/`, re-take if you edit)
- [x] login, dashboard, candidates, candidate-form, candidate-details, companies
- [x] jobs, job-form, applications, interviews, placement-process, reports
