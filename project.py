import re
import json
from datetime import datetime


class Member:  #! MEMBER CLASS
    members = []

    def __init__(self, first_name, last_name, email_address, user_password, contact_number):  #! CONSTRUCTOR
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.user_password = user_password
        self.contact_number = contact_number
        self.initiatives = []  #! INITIATIVES LIST

    @staticmethod
    def validate_contact(contact_number):  #! CONTACT NUMBER VALIDATION
        return re.fullmatch(r"01[0125]\d{8}", contact_number) is not None

    @staticmethod
    def signup():  #! SIGNUP FUNCTION
        print("\nSign up as a new member")
        first_name = input("First name: ")
        last_name = input("Last name: ")
        email_address = input("Email: ")
        user_password = input("Password: ")
        confirm_password = input("Confirm password: ")
        contact_number = input("Contact number: ")

        if user_password != confirm_password:
            print("Passwords do not match.")
            return None

        if not Member.validate_contact(contact_number):
            print("Invalid Egyptian contact number.")
            return None

        if any(member.email_address == email_address for member in Member.members):
            print("Email already in use.")
            return None

        member = Member(first_name, last_name, email_address, user_password, contact_number)
        Member.members.append(member)
        print("Sign-up successful!")
        return member

    @staticmethod
    def signin():  #! SIGN-IN FUNCTION
        print("\nSign in")
        email_address = input("Email: ")
        user_password = input("Password: ")

        for member in Member.members:
            if member.email_address == email_address and member.user_password == user_password:
                print("Sign-in successful!")
                return member

        print("Invalid email or password.")
        return None

    def to_dict(self):  #! CONVERT TO DICTIONARY
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "user_password": self.user_password,
            "contact_number": self.contact_number,
            "initiatives": [initiative.to_dict() for initiative in self.initiatives],
        }

    @staticmethod
    def from_dict(data):  #! CONVERT DICTIONARY TO OBJECT
        member = Member(
            data["first_name"], data["last_name"], data["email_address"], data["user_password"], data["contact_number"]
        )
        member.initiatives = [Initiative.from_dict(initiative) for initiative in data["initiatives"]]
        return member


class Initiative:  #! INITIATIVE CLASS
    def __init__(self, name, description, funding_goal, launch_date, completion_date):
        self.name = name
        self.description = description
        self.funding_goal = funding_goal
        self.launch_date = launch_date
        self.completion_date = completion_date

    @staticmethod
    def validate_date(date_string):  #! DATE VALIDATION
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def create_initiative():
        print("\nStart a new initiative")
        name = input("Name: ")
        description = input("Description: ")
        try:
            funding_goal = float(input("Funding goal (EGP): "))
        except ValueError:
            print("Invalid funding goal.")
            return None

        launch_date = input("Launch date (YYYY-MM-DD): ")
        completion_date = input("Completion date (YYYY-MM-DD): ")

        if not Initiative.validate_date(launch_date) or not Initiative.validate_date(completion_date):
            print("Invalid date format.")
            return None

        if datetime.strptime(launch_date, '%Y-%m-%d') >= datetime.strptime(completion_date, '%Y-%m-%d'):
            print("Completion date must be after launch date.")
            return None

        return Initiative(name, description, funding_goal, launch_date, completion_date)

    def display(self):
        print(f"\nName: {self.name}")
        print(f"Description: {self.description}")
        print(f"Funding Goal: {self.funding_goal} EGP")
        print(f"Launch Date: {self.launch_date}")
        print(f"Completion Date: {self.completion_date}")

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "funding_goal": self.funding_goal,
            "launch_date": self.launch_date,
            "completion_date": self.completion_date,
        }

    @staticmethod
    def from_dict(data):
        return Initiative(data["name"], data["description"], data["funding_goal"], data["launch_date"], data["completion_date"])


class Platform:
    DATA_FILE = "platform_data.json"

    def __init__(self):
        self.active_member = None
        self.load_data()

    def main_menu(self):
        while True:
            print("\n--- Welcome to the Crowdfunding Platform ---")
            print("1. Sign Up")
            print("2. Sign In")
            print("3. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                self.active_member = Member.signup()
            elif choice == '2':
                self.active_member = Member.signin()
                if self.active_member:
                    self.member_menu()
            elif choice == '3':
                self.save_data()
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

    def member_menu(self):
        while True:
            print("\n--- Member Menu ---")
            print("1. Start Initiative")
            print("2. View My Initiatives")
            print("3. Update Initiative")
            print("4. Remove Initiative")
            print("5. Sign Out")
            choice = input("Choose an option: ")

            if choice == '1':
                initiative = Initiative.create_initiative()
                if initiative:
                    self.active_member.initiatives.append(initiative)
                    print("Initiative started successfully.")
            elif choice == '2':
                self.view_initiatives()
            elif choice == '3':
                self.update_initiative()
            elif choice == '4':
                self.remove_initiative()
            elif choice == '5':
                print("Signing out...")
                break
            else:
                print("Invalid choice.")

    def view_initiatives(self):
        if not self.active_member.initiatives:
            print("You have no initiatives.")
        else:
            print("\nYour Initiatives:")
            for i, initiative in enumerate(self.active_member.initiatives):
                print(f"\nInitiative {i + 1}:")
                initiative.display()

    def update_initiative(self):
        self.view_initiatives()
        if not self.active_member.initiatives:
            return

        try:
            initiative_index = int(input("Enter the initiative number to update: ")) - 1
            if 0 <= initiative_index < len(self.active_member.initiatives):
                initiative = self.active_member.initiatives[initiative_index]
                print("\nUpdating initiative:")
                initiative.display()

                print("\nEnter new details (leave blank to keep current value):")
                name = input(f"New Name [{initiative.name}]: ") or initiative.name
                description = input(f"New Description [{initiative.description}]: ") or initiative.description

                try:
                    funding_goal = input(f"New Funding Goal [{initiative.funding_goal}]: ")
                    funding_goal = float(funding_goal) if funding_goal else initiative.funding_goal
                except ValueError:
                    print("Invalid funding goal.")
                    return

                launch_date = input(f"New Launch Date [{initiative.launch_date}]: ") or initiative.launch_date
                completion_date = input(f"New Completion Date [{initiative.completion_date}]: ") or initiative.completion_date

                if not Initiative.validate_date(launch_date) or not Initiative.validate_date(completion_date):
                    print("Invalid date format.")
                    return

                if datetime.strptime(launch_date, '%Y-%m-%d') >= datetime.strptime(completion_date, '%Y-%m-%d'):
                    print("Completion date must be after launch date.")
                    return

                initiative.name = name
                initiative.description = description
                initiative.funding_goal = funding_goal
                initiative.launch_date = launch_date
                initiative.completion_date = completion_date

                print("Initiative updated successfully.")
            else:
                print("Invalid initiative number.")
        except ValueError:
            print("Invalid input.")

    def remove_initiative(self):
        self.view_initiatives()
        if not self.active_member.initiatives:
            return

        try:
            initiative_index = int(input("Enter the initiative number to remove: ")) - 1
            if 0 <= initiative_index < len(self.active_member.initiatives):
                self.active_member.initiatives.pop(initiative_index)
                print("Initiative removed successfully.")
            else:
                print("Invalid initiative number.")
        except ValueError:
            print("Invalid input.")

    def save_data(self):
        with open(self.DATA_FILE, 'w') as file:
            json.dump([member.to_dict() for member in Member.members], file)
        print("Data saved successfully.")

    def load_data(self):
        try:
            with open(self.DATA_FILE, 'r') as file:
                data = json.load(file)
                Member.members = [Member.from_dict(member) for member in data]
            print("Data loaded successfully.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No previous data found. Starting fresh.")


if __name__ == "__main__":
    platform = Platform()
    platform.main_menu()
