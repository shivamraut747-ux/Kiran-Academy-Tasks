# Phase 2 changes

## New
- Company: model, DAO, service, console menu (add, update, search, view, activate/deactivate)
- Job: create (with skills, in one transaction), update, search, view open jobs, close
- Candidate: update, search, view details, deactivate (soft), auto-generated candidate code
- Console login (users table), current user is remembered for created_by / changed_by
- Helpers: `fetch_all`, `fetch_one`, `execute`, `transaction()` in `util/db_connection.py`;
  `util/console_input.py`, `util/display.py`, `util/session.py`
- More exceptions: ValidationError, DuplicateRecordError, CompanyNotFoundError, LoginError
- 10 more sample candidates (30 total) + their skills
- `tests/test_phase2.py` (18 tests)

## Changed in existing files
- `app/main.py`: 9-option menu from the spec; old "Apply for Job" moved to Applications,
  old technology report moved to Reports
- `service/candidate_service.py`: messages now match the UI spec; errors use ValidationError
  (it is a ValueError, so old code still works)
- `dao/candidate_dao.py`, `dao/job_dao.py`: new methods added, old methods untouched
- `model/*.py`: extra optional fields added
- `service/activity_log_service.py`: log file always in the project folder, readable timestamp
- `sql/rpms_sample_data.sql`, `sql/rpms_full_setup.sql`: +10 candidates

## Run
    python main.py
    python -m unittest tests.test_phase2 -v
