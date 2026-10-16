import random

# cab types and their per km rates
cabs = {
    "1": ["Auto", 12],
    "2": ["Sedan", 18],
    "3": ["SUV", 25],
}

# source, destination, distance in km
routes = {
    "1": ["Pune Station", "Shivajinagar", 5],
    "2": ["Swargate", "Kothrud", 8],
    "3": ["Hinjawadi", "Wakad", 10],
}


def book_ride():
    print("\nChoose cab type:")
    for key in cabs:
        print(key + ". " + cabs[key][0] + " (Rs " + str(cabs[key][1]) + "/km)")

    cab_choice = input("Your choice: ").strip()
    if cab_choice not in cabs:
        print("Invalid choice, going back to menu.")
        return

    cab_name = cabs[cab_choice][0]
    rate = cabs[cab_choice][1]

    print("\nChoose route:")
    for key in routes:
        r = routes[key]
        print(f"{key}. {r[0]} to {r[1]} ({r[2]} km)")

    route_choice = input("Your choice: ").strip()
    if route_choice not in routes:
        print("Invalid choice, going back to menu.")
        return

    source, destination, distance = routes[route_choice]
    fare = distance * rate

    print("\n--- Ride Summary ---")
    print("Cab:", cab_name)
    print("From:", source)
    print("To:", destination)
    print("Distance:", distance, "km")
    print("Rate: Rs", rate, "per km")
    print(f"Total fare: {distance} x {rate} = Rs {fare}")

    # cancel is only allowed before the otp is given
    print("\n1. Confirm and get OTP")
    print("2. Cancel")
    confirm = input("Your choice: ").strip()

    if confirm == "1":
        otp = random.randint(1000, 9999)
        print("\nYour OTP is", otp)
        print("OTP is shared now so you can't cancel this ride anymore.")
        print(f"Booked! Your {cab_name} is on the way from {source} to {destination}.")
    elif confirm == "2":
        print("\nRide cancelled.")
    else:
        print("\nInvalid choice, ride not booked.")


def main():
    print("Welcome to Cab Booking!")

    while True:
        print("\n1. Book ride")
        print("2. Exit")
        choice = input("Your choice: ").strip()

        if choice == "1":
            book_ride()
        elif choice == "2":
            print("Thanks, bye!")
            break
        else:
            print("Please enter 1 or 2.")


main()