from rpms.dao.candidate_dao import CandidateDAO
from rpms.dao.company_dao import CompanyDAO
from rpms.dao.job_dao import JobDAO
from rpms.dao.skill_dao import SkillDAO
from rpms.dao.user_dao import UserDAO
from rpms.dao.application_dao import ApplicationDAO
from rpms.dao.application_history_dao import ApplicationHistoryDAO

from rpms.service.candidate_service import CandidateService
from rpms.service.company_service import CompanyService
from rpms.service.job_service import JobService
from rpms.service.user_service import UserService
from rpms.service.eligibility_service import EligibilityService
from rpms.service.application_service import ApplicationService
from rpms.service.report_service import ReportService
from rpms.service.activity_log_service import ActivityLogService

from rpms.app.candidate_menu import candidate_menu
from rpms.app.company_menu import company_menu
from rpms.app.job_menu import job_menu
from rpms.app.report_menu import reports_menu
from rpms.app.application_menu import applications_menu
from rpms.app.interview_menu import interview_menu
from rpms.app.offer_placement_menu import offer_menu, placement_menu
from rpms.dao.interview_dao import InterviewDAO
from rpms.dao.offer_dao import OfferDAO
from rpms.dao.placement_dao import PlacementDAO
from rpms.service.interview_service import InterviewService
from rpms.service.offer_service import OfferService
from rpms.service.placement_service import PlacementService

from rpms.exception.exceptions import LoginError
from rpms.util.console_input import ask_int
from rpms.util.session import set_current_user, get_current_user


def print_menu():
    print("\n==================================")
    print("RECRUITMENT & PLACEMENT SYSTEM")
    print("==================================")
    user = get_current_user()
    if user:
        print(f"Logged in as: {user.full_name} ({user.role_name})")
        print("----------------------------------")
    print("1. Candidates")
    print("2. Companies")
    print("3. Jobs")
    print("4. Applications")
    print("5. Interviews")
    print("6. Offers")
    print("7. Placements")
    print("8. Reports")
    print("9. Exit")


def login(user_service, log_service):
    """Simple login: choose one of the ACTIVE users. Three attempts."""
    print("\n=== LOGIN ===")
    print("Active users:")
    for u in user_service.get_active_users():
        print(f"  {u.username:<18} {u.role_name}")
    for _ in range(3):
        username = input("Username: ").strip()
        try:
            user = user_service.login(username)
        except LoginError as exc:
            print("Login failed:", exc)
            continue
        set_current_user(user)
        log_service.log(f"User Login: {user.username}")
        return True
    return False


def main():
    # --- build objects: DAO (database) -> Service (rules) ---
    candidate_dao = CandidateDAO()
    company_dao = CompanyDAO()
    job_dao = JobDAO()
    skill_dao = SkillDAO()
    user_dao = UserDAO()
    application_dao = ApplicationDAO()
    history_dao = ApplicationHistoryDAO()

    candidate_service = CandidateService(candidate_dao)
    company_service = CompanyService(company_dao)
    job_service = JobService(job_dao, company_dao, skill_dao)
    user_service = UserService(user_dao)
    eligibility_service = EligibilityService()
    application_service = ApplicationService(
        candidate_dao, job_dao, application_dao, eligibility_service, history_dao
    )
    interview_dao, offer_dao, placement_dao = InterviewDAO(), OfferDAO(), PlacementDAO()
    interview_service = InterviewService(interview_dao, application_dao, application_service)
    offer_service = OfferService(offer_dao, application_dao, placement_dao, application_service)
    placement_service = PlacementService(placement_dao, offer_dao, application_service)
    report_service = ReportService()
    log_service = ActivityLogService()

    try:
        if not login(user_service, log_service):
            print("Too many failed attempts. Exiting.")
            return
    except Exception as exc:
        print("ERROR:", exc)
        return

    while True:
        print_menu()
        choice = input("Enter Choice: ").strip()

        if choice == "1":
            candidate_menu(candidate_service, log_service)
        elif choice == "2":
            company_menu(company_service, log_service)
        elif choice == "3":
            job_menu(job_service, company_service, skill_dao, log_service)
        elif choice == "4":
            applications_menu(application_service, log_service)
        elif choice == "5":
            interview_menu(interview_service, log_service)
        elif choice == "6":
            offer_menu(offer_service, log_service)
        elif choice == "7":
            placement_menu(placement_service, log_service)
        elif choice == "8":
            reports_menu(report_service, log_service)
        elif choice == "9":
            print("Application closed.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
