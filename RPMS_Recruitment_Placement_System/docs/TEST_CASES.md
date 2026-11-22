# Test Cases

Login for manual tests: `amit.recruiter`. Load `sql/rpms_full_setup.sql` first.
**Result** column: Pass / Fail after running.

## A. Automated (run `python -m unittest discover -s tests -v`)

Last run: 38 tests, all passed (OK).

| ID | File | What it checks | Result |
|---|---|---|---|
| A1 | test_phase2 | Candidate add/update/search/deactivate, duplicate email & mobile blocked, validation messages | Pass |
| A2 | test_phase2 | Job create with skills, unknown skill saves nothing, rollback when 2nd table fails, login | Pass |
| A3 | test_phase3 | Valid status steps allowed; jumps (APPLIED→JOINED) blocked; unknown status | Pass |
| A4 | test_phase3 | Full apply→shortlist→reject flow; history row on each change; rollback if history insert fails | Pass |
| A5 | test_phase4 | Interview rules, full offer→placement flow, rejected offer closes application, joining rollback, rollback demo | Pass |
| A6 | test_phase5 | All 13 reports run; totals agree (placed + unplaced = all candidates, etc.) | Pass |

## B. Manual (console)
| ID | Module | Steps | Expected | Result |
|---|---|---|---|---|
| B1 | Login | Valid user | Menu appears | Pass |
| B2 | Login | Wrong user 3 times | "Too many failed attempts", exit | |
| B3 | Candidate | Add valid candidate | Saved, code CAN-YYYY-nnnn shown | |
| B4 | Candidate | Add with existing email | Duplicate error, nothing saved | |
| B5 | Candidate | Add with existing mobile | Duplicate error | |
| B6 | Candidate | Percentage 150 | Validation error | |
| B7 | Candidate | Invalid email format | Validation error | |
| B8 | Candidate | Search by technology | Only matching candidates listed | |
| B9 | Candidate | Update then view | Changes visible | |
| B10 | Candidate | Deactivate twice | 2nd attempt rejected | |
| B11 | Company | Add valid company | Saved with code | |
| B12 | Company | Add with missing name | Validation error | |
| B13 | Job | Create job with skills | Job + skills saved | |
| B14 | Job | Create with unknown skill | Nothing saved (rollback) | |
| B15 | Job | Create for inactive company | Blocked | |
| B16 | Job | Deadline before posted date | Validation error | |
| B17 | Job | Close job | Status CLOSED | |
| B18 | Application | Apply eligible candidate to open job | APPLIED + history NULL→APPLIED | Pass |
| B19 | Application | Apply same candidate/job again | Duplicate blocked | |
| B20 | Application | Apply after deadline | Blocked | Pass |
| B21 | Application | Apply with too many backlogs / low % | Marked not eligible / blocked with reason | |
| B22 | Application | Shortlist APPLIED application | SHORTLISTED + history row | |
| B23 | Application | Reject without reason | Reason required error | |
| B24 | Application | Shortlist a REJECTED application | Invalid transition error | |
| B25 | Application | Withdraw | WITHDRAWN, final | |
| B26 | Application | View History | All changes in order | |
| B27 | Interview | Schedule for SHORTLISTED app | Round 1 created, app INTERVIEW_SCHEDULED | |
| B28 | Interview | Schedule in the past | Blocked | |
| B29 | Interview | Schedule for APPLIED app | Blocked | |
| B30 | Interview | Round 2 while round 1 open | Blocked | |
| B31 | Interview | Feedback rating 6 | Rating 0–5 error | |
| B32 | Interview | Feedback SELECTED | Interview COMPLETED, app SELECTED | |
| B33 | Interview | Feedback REJECTED | App REJECTED | |
| B34 | Interview | Mark no-show, schedule new round | Allowed | |
| B35 | Offer | Create offer for non-SELECTED app | Blocked | |
| B36 | Offer | Create offer for SELECTED app | OFFERED, app OFFERED | |
| B37 | Offer | Duplicate offer for same app | Blocked | |
| B38 | Offer | Update to ACCEPTED | Status ACCEPTED | |
| B39 | Offer | Update to EXPIRED/WITHDRAWN/REJECTED | App closed as REJECTED | |
| B40 | Placement | Confirm joining without ACCEPTED offer | Blocked | |
| B41 | Placement | Confirm joining (JOINED) | Candidate PLACED, app JOINED | |
| B42 | Placement | Rollback demo (option 4) | Error shown, value unchanged | |
| B43 | Reports | Run each of 13 reports | Table printed, no error | |
| B44 | Reports | Applications by Status total | Equals row count of applications | |
| B45 | Reports | Company-wise vs Technology-wise placements | Both sum to joined total | |
| B46 | Reports | View a report | Line added to `activity_log.txt` | |
| B47 | Menu | Enter invalid menu choice | "Invalid choice", no crash | |
| B48 | DB | Stop MySQL, start app | Friendly error, no traceback crash | |
