"""
Demo / driver script for the Project Management System.
Run with:  python3 demo.py
"""
from datetime import date
from pms import (
    Company, Employee, Client,
    WebDevelopmentProject, MobileAppProject, DataScienceProject,
)


def main():
    company = Company("BrightWave Technologies")

    # ---- Employees ----
    alice = Employee("Alice Fernandes", "Project Lead", ["Scrum", "Java", "Communication"])
    bob = Employee("Bob D'Souza", "Backend Developer", ["Python", "Django", "PostgreSQL"])
    carol = Employee("Carol Nair", "Frontend Developer", ["React", "CSS", "TypeScript"])
    dave = Employee("Dave Mehta", "Data Scientist", ["Python", "ML", "Pandas"])
    for e in (alice, bob, carol, dave):
        company.hire_employee(e)

    # ---- Clients ----
    client_a = Client("Rohan Kapoor", "rohan@acme.com", "Acme Retail Pvt Ltd")
    client_b = Client("Meera Iyer", "meera@finserv.com", "FinServ Solutions")
    company.onboard_client(client_a)
    company.onboard_client(client_b)

    # ---- Project 1: Web Development ----
    web_project = WebDevelopmentProject(
        name="Acme E-commerce Portal",
        client=client_a,
        budget=8000,
        deadline=date(2026, 9, 30),
    )
    web_project.add_requirement("User authentication & login", "High")
    web_project.add_requirement("Product catalog with search", "High")
    web_project.add_requirement("Payment gateway integration", "Medium")
    web_project.assign_employee(alice, "Project Lead")
    web_project.assign_employee(bob, "Backend Developer")
    web_project.assign_employee(carol, "Frontend Developer")
    company.register_project(web_project)

    # ---- Project 2: Mobile App ----
    mobile_project = MobileAppProject(
        name="FinServ Customer App",
        client=client_b,
        budget=12000,
        deadline=date(2026, 11, 15),
        platforms=["Android", "iOS"],
    )
    mobile_project.add_requirement("Biometric login", "High")
    mobile_project.add_requirement("Push notifications", "Medium")
    mobile_project.assign_employee(alice, "Project Lead")
    mobile_project.assign_employee(carol, "Mobile UI Developer")
    company.register_project(mobile_project)

    # ---- Project 3: Data Science ----
    ds_project = DataScienceProject(
        name="Acme Customer Churn Prediction",
        client=client_a,
        budget=6000,
        deadline=date(2026, 10, 20),
        dataset_size_gb=75,
    )
    ds_project.add_requirement("Clean & merge 3 years of sales data", "High")
    ds_project.add_requirement("Build churn prediction model", "High")
    ds_project.assign_employee(dave, "Data Scientist")
    company.register_project(ds_project)

    # ---- Simulate lifecycle progress + feedback at every stage ----
    for project in company.projects:
        project.add_feedback("Requirements look complete and clear.", 5)
        project.advance_stage()          # -> Testing
        project.add_feedback("Found a couple of minor bugs during UAT.", 4)
        project.advance_stage()          # -> Deployment
        project.add_feedback("Deployment went smoothly, app is live.", 5)
        project.advance_stage()          # -> Maintenance
        project.add_feedback("Support response time has been great.", 5)

    # ---- Record partial payments ----
    web_project.billing.record_payment(4000)
    mobile_project.billing.record_payment(mobile_project.calculate_billing())
    ds_project.billing.record_payment(2000)

    # ---- Print full reports ----
    print(company.company_summary())
    print()
    for project in company.projects:
        print(project.generate_report())
        print(f"Final Billing Amount (polymorphic calculate_billing()): "
              f"Rs.{project.calculate_billing():.2f}")
        print()


if __name__ == "__main__":
    main()
