from rpms.model.company import Company
from rpms.util.console_input import ask_text, ask_int, ask_choice, ask_yes_no
from rpms.util.display import print_table

COMPANY_TYPES = ("MNC", "STARTUP", "MID_SIZE", "CONSULTANCY")


def show_companies(companies):
    rows = [(c.company_id, c.company_code, c.company_name, c.industry, c.location,
             c.company_type, c.hr_name, c.status, f"{c.open_jobs} Open Jobs")
            for c in companies]
    print_table(["ID", "Code", "Company", "Industry", "Location", "Type", "HR", "Status", "Jobs"], rows)


def read_company(current: Company | None = None) -> Company:
    c = current or Company()
    result = Company(company_id=c.company_id, company_code=c.company_code)
    result.company_name = ask_text("Company Name", c.company_name, required=True)
    result.industry = ask_text("Industry", c.industry, required=True)
    result.website = ask_text("Website", c.website)
    result.location = ask_text("Location", c.location, required=True)
    result.company_type = ask_choice("Company Type", COMPANY_TYPES, c.company_type or None)
    result.hr_name = ask_text("HR Name", c.hr_name, required=True)
    result.hr_email = ask_text("HR Email", c.hr_email, required=True)
    result.hr_mobile = ask_text("HR Mobile (10 digits, optional)", c.hr_mobile)
    result.status = ask_choice("Status", ("ACTIVE", "INACTIVE"), c.status if current else "ACTIVE")
    return result


def company_menu(company_service, log_service):
    while True:
        print("\n------ COMPANIES ------")
        print("1. View All Companies")
        print("2. Add Company")
        print("3. Update Company")
        print("4. Search Companies")
        print("5. Activate / Deactivate Company")
        print("0. Back")
        choice = input("Enter Choice: ").strip()

        try:
            if choice == "1":
                show_companies(company_service.get_all_companies())

            elif choice == "2":
                company = read_company()
                company_id = company_service.add_company(company)
                print(f"Company created. ID = {company_id}, Code = {company.company_code}")
                log_service.log(f"Company Created: {company.company_code}")

            elif choice == "3":
                company_id = ask_int("Company ID to update", required=True)
                current = company_service.get_company(company_id)
                print("Press Enter to keep the value shown in [brackets].")
                company_service.update_company(read_company(current))
                print("Company updated.")
                log_service.log(f"Company Updated: {current.company_code}")

            elif choice == "4":
                print("Leave a box empty to skip it.")
                filters = {
                    "name": ask_text("Company Name"),
                    "location": ask_text("Location"),
                    "company_type": ask_choice("Company Type", COMPANY_TYPES, required=False),
                    "status": ask_choice("Status", ("ACTIVE", "INACTIVE"), required=False),
                }
                show_companies(company_service.search_companies(filters))

            elif choice == "5":
                company_id = ask_int("Company ID", required=True)
                company = company_service.get_company(company_id)
                new_status = "INACTIVE" if company.status == "ACTIVE" else "ACTIVE"
                if ask_yes_no(f"Change {company.company_name} from {company.status} to {new_status}?"):
                    company_service.set_status(company_id, new_status)
                    print(f"Company is now {new_status}.")
                    log_service.log(f"Company {new_status}: {company.company_code}")
                else:
                    print("Cancelled.")

            elif choice == "0":
                return
            else:
                print("Invalid choice.")
        except Exception as exc:
            print("ERROR:", exc)
