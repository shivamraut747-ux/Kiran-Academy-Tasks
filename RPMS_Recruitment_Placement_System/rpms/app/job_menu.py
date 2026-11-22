from datetime import date

from rpms.model.job import Job
from rpms.util.console_input import (
    ask_text, ask_int, ask_float, ask_date, ask_choice, ask_yes_no
)
from rpms.util.display import print_table
from rpms.util.session import get_current_user_id

EMPLOYMENT_TYPES = ("FULL_TIME", "INTERNSHIP", "CONTRACT")
STATUSES = ("DRAFT", "OPEN", "CLOSED", "CANCELLED")


def show_jobs(jobs):
    rows = []
    for j in jobs:
        package = f"{j.min_package_lpa:g}-{j.max_package_lpa:g}" if j.max_package_lpa else "-"
        rows.append((j.job_id, j.job_code, j.company_name, j.job_title, j.skills or "-",
                     j.openings, j.location, package, j.application_deadline, j.status))
    print_table(["ID", "Job Code", "Company", "Title", "Skills", "Openings", "Location",
                 "LPA", "Deadline", "Status"], rows)


def read_job(current: Job | None = None) -> Job:
    """Asks all job fields. If 'current' is given (update), Enter keeps the old value."""
    j = current or Job()
    result = Job(job_id=j.job_id, job_code=j.job_code, company_id=j.company_id)
    result.job_title = ask_text("Job Title", j.job_title, required=True)
    result.employment_type = ask_choice("Employment Type", EMPLOYMENT_TYPES, j.employment_type)
    result.location = ask_text("Location", j.location, required=True)
    result.openings = ask_int("Number of Openings", j.openings or None, required=True)
    result.min_package_lpa = ask_float("Minimum Package (LPA, optional)", j.min_package_lpa or None) or 0.0
    result.max_package_lpa = ask_float("Maximum Package (LPA, optional)", j.max_package_lpa or None) or 0.0
    result.min_percentage = ask_float("Minimum Percentage", j.min_percentage if current else None, required=True)
    result.min_passing_year = ask_int("Minimum Passing Year (optional)", j.min_passing_year or None) or 0
    result.max_passing_year = ask_int("Maximum Passing Year (optional)", j.max_passing_year or None) or 0
    result.max_backlogs = ask_int("Maximum Backlogs", j.max_backlogs if current else None, required=True)
    result.qualification_rule = ask_text("Qualification Rule (example: BE/BTech/MCA)", j.qualification_rule)
    result.posted_date = ask_date("Posted Date", j.posted_date or date.today().isoformat(), required=True)
    result.application_deadline = ask_date("Application Deadline", j.application_deadline, required=True)
    result.status = ask_choice("Status", STATUSES, j.status if current else "OPEN")
    return result


def ask_skills(skill_dao, current=None):
    print("Available skills: " + ", ".join(s["skill_name"] for s in skill_dao.find_all_active()))
    text = ask_text("Required Skills (comma separated)", current)
    return [name.strip() for name in text.split(",") if name.strip()]


def job_menu(job_service, company_service, skill_dao, log_service):
    while True:
        print("\n------ JOBS ------")
        print("1. View Open Jobs")
        print("2. Create Job")
        print("3. Update Job")
        print("4. Search Jobs")
        print("5. Close Job")
        print("0. Back")
        choice = input("Enter Choice: ").strip()

        try:
            if choice == "1":
                show_jobs(job_service.get_open_jobs())

            elif choice == "2":
                from rpms.app.company_menu import show_companies
                show_companies(company_service.search_companies({"status": "ACTIVE"}))
                company_id = ask_int("Company ID for this job", required=True)
                job = read_job()
                job.company_id = company_id
                skills = ask_skills(skill_dao)
                job_id, job_code = job_service.create_job(job, skills, get_current_user_id())
                print(f"Job created. ID = {job_id}, Code = {job_code}")
                log_service.log(f"Job Created: {job_code}")

            elif choice == "3":
                job_id = ask_int("Job ID to update", required=True)
                current = job_service.get_job_details(job_id)
                print("Press Enter to keep the value shown in [brackets].")
                updated = read_job(current)
                skills = ask_skills(skill_dao, current.skills)
                job_service.update_job(updated, skills)
                print("Job updated.")
                log_service.log(f"Job Updated: {current.job_code}")

            elif choice == "4":
                print("Leave a box empty to skip it.")
                filters = {
                    "job_code": ask_text("Job Code"),
                    "company_id": ask_int("Company ID"),
                    "technology": ask_text("Skill / Technology"),
                    "location": ask_text("Location"),
                    "status": ask_choice("Status", STATUSES, required=False),
                    "employment_type": ask_choice("Employment Type", EMPLOYMENT_TYPES, required=False),
                }
                show_jobs(job_service.search_jobs(filters))

            elif choice == "5":
                job_id = ask_int("Job ID to close", required=True)
                job = job_service.get_job(job_id)
                if ask_yes_no(f"Close job {job.job_code} - {job.job_title}?"):
                    job_service.close_job(job_id)
                    print("Job is now CLOSED.")
                    log_service.log(f"Job Closed: {job.job_code}")
                else:
                    print("Cancelled.")

            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)
