# Phase 3 - Application workflow

## New files
- rpms/util/workflow.py - allowed status transitions (no database code)
- rpms/dao/application_history_dao.py - insert/read application_history
- rpms/app/application_menu.py - Applications menu (8 options)
- tests/test_phase3.py - workflow, history and rollback tests

## Changed files (and why)
- rpms/exception/exceptions.py - added ApplicationNotFoundError, InvalidStatusTransitionError
- rpms/dao/application_dao.py - old methods untouched; added next_code, save_tx, find_by_id (FOR UPDATE), update_status, update_eligibility, search, count_by_status (all accept con for transactions)
- rpms/service/application_service.py - apply_for_job now saves application + first history row in ONE transaction; new change_status (single place for all status changes), shortlist, reject, withdraw, verify_eligibility, search, get_history, status_summary
- rpms/app/main.py - uses the new Applications menu
- Application codes are now APP-2026-0041 style (were random hex)

## Workflow (Database PDF statuses)
APPLIED -> ELIGIBILITY_VERIFIED (optional) -> SHORTLISTED -> INTERVIEW_SCHEDULED -> INTERVIEWED -> SELECTED -> OFFERED -> JOINED
REJECTED / WITHDRAWN allowed from any non-final status. JOINED, REJECTED, WITHDRAWN are final.
INTERVIEWED -> INTERVIEW_SCHEDULED is allowed for the next round.
APPLIED -> SHORTLISTED is allowed directly (Technical Spec); ELIGIBILITY_VERIFIED is optional.

## Test
python -m unittest tests.test_phase3 -v      (3 rule tests need no DB; 3 DB tests need MySQL)
