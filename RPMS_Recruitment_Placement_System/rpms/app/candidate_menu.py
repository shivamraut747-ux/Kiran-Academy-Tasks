from rpms.model.candidate import Candidate
from rpms.util.console_input import ask_text, ask_int, ask_float, ask_choice, ask_yes_no
from rpms.util.display import print_table

TECHNOLOGIES = ("Java", "Python", "Testing", "Data Analytics")


def show_candidates(candidates):
    rows = [(c.candidate_id, c.candidate_code, c.full_name, c.primary_technology,
             c.qualification, c.passing_year, c.percentage, c.backlog_count,
             c.profile_status, c.placement_status) for c in candidates]
    print_table(["ID", "Code", "Name", "Technology", "Qual.", "Year", "%", "Backlogs",
                 "Status", "Placement"], rows)


def show_candidate_details(c):
    print(f"\n--- {c.candidate_code} | {c.full_name} | {c.profile_status} ---")
    print(f"Email: {c.email}    Mobile: {c.mobile}")
    print(f"Qualification: {c.qualification}    College: {c.college or '-'}    University: {c.university or '-'}")
    print(f"Passing Year: {c.passing_year}    Percentage: {c.percentage}    Backlogs: {c.backlog_count}")
    print(f"Primary Technology: {c.primary_technology}    Placement: {c.placement_status}")
    print(f"Current Location: {c.current_location or '-'}    Preferred Location: {c.preferred_location or '-'}")


def read_candidate(current: Candidate | None = None) -> Candidate:
    """Asks all fields. If 'current' is given (update), Enter keeps the old value."""
    c = current or Candidate()
    result = Candidate(candidate_id=c.candidate_id, candidate_code=c.candidate_code,
                       placement_status=c.placement_status)
    result.full_name = ask_text("Full Name", c.full_name, required=True)
    result.email = ask_text("Email", c.email, required=True)
    result.mobile = ask_text("Mobile (10 digits)", c.mobile, required=True)
    result.qualification = ask_text("Qualification (BE/BTech/MCA/BCA/BSc...)", c.qualification, required=True)
    result.college = ask_text("College", c.college)
    result.university = ask_text("University", c.university)
    result.passing_year = ask_int("Passing Year", c.passing_year or None, required=True)
    result.percentage = ask_float("Percentage", c.percentage if current else None, required=True)
    result.backlog_count = ask_int("Backlog Count", c.backlog_count if current else None, required=True)
    result.primary_technology = ask_choice("Primary Technology", TECHNOLOGIES, c.primary_technology or None)
    result.current_location = ask_text("Current Location", c.current_location)
    result.preferred_location = ask_text("Preferred Location", c.preferred_location)
    if current:
        result.profile_status = ask_choice("Profile Status", ("ACTIVE", "INACTIVE", "ON_HOLD"),
                                           c.profile_status if c.profile_status != "BLACKLISTED" else None)
    return result


def search_filters():
    print("Leave a box empty to skip it.")
    return {
        "candidate_code": ask_text("Candidate Code"),
        "full_name": ask_text("Name"),
        "mobile": ask_text("Mobile"),
        "email": ask_text("Email"),
        "technology": ask_choice("Technology", TECHNOLOGIES, required=False),
        "passing_year": ask_int("Passing Year"),
        "qualification": ask_text("Qualification"),
        "status": ask_choice("Status", ("ACTIVE", "INACTIVE", "ON_HOLD", "PLACED"), required=False),
    }


def candidate_menu(candidate_service, log_service):
    while True:
        print("\n------ CANDIDATES ------")
        print("1. View All Candidates")
        print("2. Add Candidate")
        print("3. Update Candidate")
        print("4. Search Candidates")
        print("5. View Candidate Details")
        print("6. Deactivate Candidate")
        print("0. Back")
        choice = input("Enter Choice: ").strip()

        try:
            if choice == "1":
                show_candidates(candidate_service.get_all_candidates())

            elif choice == "2":
                candidate = read_candidate()
                candidate_id = candidate_service.add_candidate(candidate)
                print(f"Candidate created. ID = {candidate_id}, Code = {candidate.candidate_code}")
                log_service.log(f"Candidate Created: {candidate.candidate_code}")

            elif choice == "3":
                candidate_id = ask_int("Candidate ID to update", required=True)
                current = candidate_service.get_candidate(candidate_id)
                print("Press Enter to keep the value shown in [brackets].")
                updated = read_candidate(current)
                candidate_service.update_candidate(updated)
                print("Candidate updated.")
                log_service.log(f"Candidate Updated: {current.candidate_code}")

            elif choice == "4":
                show_candidates(candidate_service.search_candidates(search_filters()))

            elif choice == "5":
                candidate_id = ask_int("Candidate ID", required=True)
                show_candidate_details(candidate_service.get_candidate(candidate_id))

            elif choice == "6":
                candidate_id = ask_int("Candidate ID to deactivate", required=True)
                candidate = candidate_service.get_candidate(candidate_id)
                if ask_yes_no(f"Deactivate {candidate.full_name} ({candidate.candidate_code})?"):
                    candidate_service.deactivate_candidate(candidate_id)
                    print("Candidate is now INACTIVE.")
                    log_service.log(f"Candidate Deactivated: {candidate.candidate_code}")
                else:
                    print("Cancelled.")

            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)
