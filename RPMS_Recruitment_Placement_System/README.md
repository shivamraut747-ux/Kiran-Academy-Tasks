# Recruitment & Placement Management System (RPMS)

Python 3 + MySQL console application. Architecture: **Main/Menu → Service → DAO → MySQL**.

## Modules
1. Candidate Management  2. Company Management  3. Job Management  4. Applications (eligibility, shortlist, reject, withdraw, history)
5. Interviews (schedule, feedback)  6. Offers  7. Placements  8. Reports (13)  9. Exit

## Requirements
Python 3 and MySQL Server installed on your computer.

## Setup
```bash
py -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```
1. **Set your MySQL password** in `rpms/util/db_connection.py` before running (host, user and password; the default password is `root`). Database name: `recruitment_portal`.
2. Load the database (this **wipes** existing data): in MySQL run `SOURCE sql/rpms_full_setup.sql;`
3. Run `python main.py`. Demo logins: `amit.recruiter`, `sneha.recruiter`, `neha.placement`, `rahul.placement`, `admin`.

## Run tests
```bash
python -m unittest discover -s tests -v
```
Tests create their own rows and delete them afterwards. They need the sample database loaded.

## HTML pages
Open `recruitment-placement-ui/login.html` in your browser, click Login, then use the left menu to visit the other pages.

## Folder map
| Path | Purpose |
|---|---|
| `main.py` | Entry point |
| `rpms/app` | Console menus |
| `rpms/service` | Business rules, transactions |
| `rpms/dao` | SQL access |
| `rpms/util/workflow.py` | Application status-transition rules |
| `rpms/exception` | Custom exceptions |
| `sql/` | Schema, sample data, full setup, `reports.sql` |
| `tests/` | Unit and database tests (phases 2–5) |
| `recruitment-placement-ui/` | 12 static HTML pages + CSS + screenshots |
| `docs/` | Data dictionary, ER diagram, test cases, screenshot checklist, phase notes |

## Key rules
- Application flow: APPLIED → (ELIGIBILITY_VERIFIED) → SHORTLISTED → INTERVIEW_SCHEDULED → INTERVIEWED → SELECTED → OFFERED → JOINED. REJECTED, WITHDRAWN, JOINED are final. Jumps are blocked.
- Every status change writes a row to `application_history` in the same transaction.
- Multi-table actions (apply, feedback, offer, joining, job + skills) commit together or roll back together.
- Duplicate applications (same candidate + job) are blocked.

## Documents
- [Test cases](docs/TEST_CASES.md) · [Data dictionary](docs/DATA_DICTIONARY.md) · [ER diagram](docs/ER_DIAGRAM.md) · [Screenshots checklist](docs/SCREENSHOTS_CHECKLIST.md)
