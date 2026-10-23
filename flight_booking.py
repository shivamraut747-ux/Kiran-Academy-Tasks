from abc import ABC, abstractmethod


class Flight:
    def __init__(self, code, airline, source, destination, seats, base_fare):
        self.__code = code
        self.__airline = airline
        self.__source = source
        self.__destination = destination
        self.__available_seats = seats
        self.__base_fare = base_fare

    @property
    def code(self):
        return self.__code

    @property
    def airline(self):
        return self.__airline

    @property
    def source(self):
        return self.__source

    @property
    def destination(self):
        return self.__destination

    @property
    def available_seats(self):
        return self.__available_seats

    @property
    def base_fare(self):
        return self.__base_fare

    def has_seats(self, count):
        return 0 < count <= self.__available_seats

    def reserve_seats(self, count):
        """Only place where seat count changes."""
        if not self.has_seats(count):
            return False
        self.__available_seats -= count
        return True

    def route(self):
        return f"{self.__source} to {self.__destination}"


class Passenger(ABC):
    def __init__(self, name, age):
        self.__name = name
        self.__age = age

    @property
    def name(self):
        return self.__name

    @property
    def age(self):
        return self.__age

    @abstractmethod
    def get_discount_percentage(self):
        pass

    @abstractmethod
    def get_type(self):
        pass


class RegularPassenger(Passenger):
    def get_discount_percentage(self):
        return 0

    def get_type(self):
        return "Regular"


class StudentPassenger(Passenger):
    def get_discount_percentage(self):
        return 10

    def get_type(self):
        return "Student"


class Booking:
    def __init__(self, booking_id, flight, passenger, tickets, subtotal, discount, final_amount):
        self.booking_id = booking_id
        self.flight = flight
        self.passenger = passenger
        self.tickets = tickets
        self.subtotal = subtotal
        self.discount = discount
        self.final_amount = final_amount

    def display_summary(self):
        p = self.passenger
        print(f"Booking ID: {self.booking_id}")
        print(f"Flight: {self.flight.code} | {self.flight.route()} ({self.flight.airline})")
        print(f"Passenger: {p.name} (Age: {p.age})")
        print(f"Passenger type: {p.get_type()}")
        print(f"Tickets: {self.tickets}")
        print(f"Base fare per ticket: ₹{self.flight.base_fare:,.0f}")
        print(f"Subtotal: ₹{self.subtotal:,.0f}")
        print(f"{p.get_type()} discount ({p.get_discount_percentage()}%): ₹{self.discount:,.0f}")
        print(f"Final amount: ₹{self.final_amount:,.0f}")


class FlightBookingSystem:
    def __init__(self):
        self.flights = [
            Flight("PN101", "Kiran Air", "Pune", "Delhi", 20, 4000),
            Flight("MB202", "Kiran Air", "Mumbai", "Bengaluru", 15, 3500),
            Flight("PH303", "Kiran Air", "Pune", "Hyderabad", 10, 2800),
        ]
        self.bookings = []
        self.__next_id = 1001

    def display_flights(self):
        print(f"\n{'Code':<8}{'Airline':<12}{'Source':<10}{'Destination':<13}{'Seats':<7}{'Fare':>8}")
        print("-" * 58)
        for f in self.flights:
            print(f"{f.code:<8}{f.airline:<12}{f.source:<10}{f.destination:<13}"
                  f"{f.available_seats:<7}{'₹' + format(f.base_fare, ','):>8}")

    def find_flight(self, code):
        for f in self.flights:
            if f.code.upper() == code.strip().upper():
                return f
        return None

    def create_passenger(self, name, age, ptype):
        if ptype.lower() == "student":
            return StudentPassenger(name, age)
        if ptype.lower() == "regular":
            return RegularPassenger(name, age)
        return None

    def validate_booking(self, flight, name, age, ptype, tickets):
        if flight is None:
            return "Flight code does not exist."
        if not name.strip():
            return "Passenger name cannot be blank."
        if age <= 0:
            return "Age must be greater than 0."
        if ptype.lower() not in ("regular", "student"):
            return "Passenger type must be Regular or Student."
        if tickets <= 0:
            return "Ticket count must be greater than 0."
        if not flight.has_seats(tickets):
            return "Not enough seats available."
        return None

    def calculate_fare(self, flight, passenger, tickets):
        subtotal = flight.base_fare * tickets
        discount = subtotal * passenger.get_discount_percentage() / 100  # polymorphism
        return subtotal, discount, subtotal - discount

    def confirm_booking(self, flight, passenger, tickets):
        subtotal, discount, final = self.calculate_fare(flight, passenger, tickets)
        if not flight.reserve_seats(tickets):
            return None
        booking = Booking(f"BK{self.__next_id}", flight, passenger, tickets, subtotal, discount, final)
        self.__next_id += 1
        self.bookings.append(booking)
        return booking

    @staticmethod
    def _read_int(prompt):
        try:
            return int(input(prompt).strip())
        except ValueError:
            return None

    def book_flight(self):
        code = input("Enter flight code: ")
        name = input("Enter passenger name: ")
        age = self._read_int("Enter age: ")
        ptype = input("Passenger type (Regular/Student): ").strip()
        tickets = self._read_int("Enter number of tickets: ")

        if age is None or tickets is None:
            print("Booking failed: Age and tickets must be whole numbers.")
            print("No booking was created. Available seats remain unchanged.")
            return

        flight = self.find_flight(code)
        error = self.validate_booking(flight, name, age, ptype, tickets)
        if error:
            print(f"Booking failed: {error}")
            print("No booking was created. Available seats remain unchanged.")
            return

        passenger = self.create_passenger(name.strip(), age, ptype)
        booking = self.confirm_booking(flight, passenger, tickets)
        print("\nBooking confirmed!")
        booking.display_summary()

    def view_booking(self):
        if not self.bookings:
            print("No bookings yet. Choose option 2 to book a flight.")
            return
        print("\nMost recent booking:")
        self.bookings[-1].display_summary()

    def run(self):
        print("Welcome to Kiran Air Booking")
        while True:
            print("\n1. View Flights\n2. Book Flight\n3. View Booking\n4. Exit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                self.display_flights()
            elif choice == "2":
                self.book_flight()
            elif choice == "3":
                self.view_booking()
            elif choice == "4":
                print("Thank you for using Kiran Air Booking!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    FlightBookingSystem().run()
