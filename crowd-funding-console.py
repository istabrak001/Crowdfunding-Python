import re
import json
from datetime import datetime


class User: #! USER CLASS
    users = []  

    def __init__(self, first_name, last_name, email, password, phone): #!CONSTRUCTOR
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone = phone
        self.projects = []  

    @staticmethod
    def validate_phone(phone): #! PHONE VALIDATION
        return re.fullmatch(r"01[0125]\d{8}", phone) is not None

    @staticmethod
    def register(): #! REGISTERATION
        print("\nRegister a new user")
        first_name = input("First name: ")
        last_name = input("Last name: ")
        email = input("Email: ")
        password = input("Password: ")
        confirm_password = input("Confirm password: ")
        phone = input("Mobile phone: ")

        if password != confirm_password:
            print("Passwords do not match.")
            return None

        if not User.validate_phone(phone):
            print("Invalid Egyptian phone number.")
            return None

        if any(user.email == email for user in User.users):
            print("Email already registered.")
            return None

        user = User(first_name, last_name, email, password, phone)
        User.users.append(user)
        print("Registration successful!")
        return user

    @staticmethod
    def login(): #! LOGIN
        print("\nLogin")
        email = input("Email: ")
        password = input("Password: ")

        for user in User.users:
            if user.email == email and user.password == password:
                print("Login successful!")
                return user

        print("Invalid email or password.")
        return None

    def to_dict(self): #! CONVERT INTO DICTIONARY
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "phone": self.phone,
            "projects": [project.to_dict() for project in self.projects],
        }

    @staticmethod
    def from_dict(data): #! FROM DICTIONARY TO AN OBJECT
        user = User(
            data["first_name"], data["last_name"], data["email"], data["password"], data["phone"]
        )
        user.projects = [Project.from_dict(project) for project in data["projects"]]
        return user


class Project: #! PROJECT CLASS
    def __init__(self, title, details, target, start_date, end_date):
        self.title = title
        self.details = details
        self.target = target
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def validate_date_format(date_text): #! DATE VALIDATION
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def create_project():
        print("\nCreate a new project")
        title = input("Title: ")
        details = input("Details: ")
        try:
            target = float(input("Total target (EGP): "))
        except ValueError:
            print("Invalid target amount.")
            return None

        start_date = input("Start date (YYYY-MM-DD): ")
        end_date = input("End date (YYYY-MM-DD): ")

        if not Project.validate_date_format(start_date) or not Project.validate_date_format(end_date):
            print("Invalid date format.")
            return None

        if datetime.strptime(start_date, '%Y-%m-%d') >= datetime.strptime(end_date, '%Y-%m-%d'):
            print("End date must be after start date.")
            return None

        return Project(title, details, target, start_date, end_date)

    def display(self):
        print(f"\nTitle: {self.title}")
        print(f"Details: {self.details}")
        print(f"Target: {self.target} EGP")
        print(f"Start Date: {self.start_date}")
        print(f"End Date: {self.end_date}")

    def to_dict(self):
        return {
            "title": self.title,
            "details": self.details,
            "target": self.target,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    @staticmethod
    def from_dict(data):
        return Project(data["title"], data["details"], data["target"], data["start_date"], data["end_date"])


class App:
    DATA_FILE = "app_data.json"

    def __init__(self):
        self.current_user = None
        self.load_data()

    def main_menu(self):
        while True:
            print("\n---Welcome to Crowdfunding App ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                self.current_user = User.register()
            elif choice == '2':
                self.current_user = User.login()
                if self.current_user:
                    self.user_menu()
            elif choice == '3':
                self.save_data()
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

    def user_menu(self):
        while True:
            print("\n--- User Menu ---")
            print("1. Create Project")
            print("2. View My Projects")
            print("3. Edit My Project")
            print("4. Delete My Project")
            print("5. Logout")
            choice = input("Choose an option: ")

            if choice == '1':
                project = Project.create_project()
                if project:
                    self.current_user.projects.append(project)
                    print("Project created successfully.")
            elif choice == '2':
                self.view_projects()
            elif choice == '3':
                self.edit_project()
            elif choice == '4':
                self.delete_project()
            elif choice == '5':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")

    def view_projects(self):
        if not self.current_user.projects:
            print("You have no projects.")
        else:
            print("\nYour Projects:")
            for i, project in enumerate(self.current_user.projects):
                print(f"\nProject {i + 1}:")
                project.display()

    def edit_project(self):
        self.view_projects()
        if not self.current_user.projects:
            return

        try:
            project_index = int(input("Enter the project number to edit: ")) - 1
            if 0 <= project_index < len(self.current_user.projects):
                project = self.current_user.projects[project_index]
                print("\nEditing project:")
                project.display()

                print("\nEnter new details (leave blank to keep current value):")
                title = input(f"New Title [{project.title}]: ") or project.title
                details = input(f"New Details [{project.details}]: ") or project.details

                try:
                    target = input(f"New Target [{project.target}]: ")
                    target = float(target) if target else project.target
                except ValueError:
                    print("Invalid target amount.")
                    return

                start_date = input(f"New Start Date [{project.start_date}]: ") or project.start_date
                end_date = input(f"New End Date [{project.end_date}]: ") or project.end_date

                if not Project.validate_date_format(start_date) or not Project.validate_date_format(end_date):
                    print("Invalid date format.")
                    return

                if datetime.strptime(start_date, '%Y-%m-%d') >= datetime.strptime(end_date, '%Y-%m-%d'):
                    print("End date must be after start date.")
                    return

                project.title = title
                project.details = details
                project.target = target
                project.start_date = start_date
                project.end_date = end_date

                print("Project updated successfully.")
            else:
                print("Invalid project number.")
        except ValueError:
            print("Invalid input.")

    def delete_project(self):
        self.view_projects()
        if not self.current_user.projects:
            return

        try:
            project_index = int(input("Enter the project number to delete: ")) - 1
            if 0 <= project_index < len(self.current_user.projects):
                self.current_user.projects.pop(project_index)
                print("Project deleted successfully.")
            else:
                print("Invalid project number.")
        except ValueError:
            print("Invalid input.")

    def save_data(self):
        with open(self.DATA_FILE, 'w') as file:
            json.dump([user.to_dict() for user in User.users], file)
        print("Data saved successfully.")

    def load_data(self):
        try:
            with open(self.DATA_FILE, 'r') as file:
                data = json.load(file)
                User.users = [User.from_dict(user) for user in data]
            print("Data loaded successfully.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No previous data found. Starting fresh.")


if __name__ == "__main__":
    app = App()
    app.main_menu()
