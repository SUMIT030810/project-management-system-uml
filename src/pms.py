"""
=====================================================================
 PROJECT MANAGEMENT SYSTEM (Object-Oriented Design)
=====================================================================
 A company handles multiple clients (projects) and assigns a
 specific set of employees to manage each project.

 Core OOP concepts demonstrated:
   - Abstraction   : Project is an abstract base class
   - Inheritance   : WebDevelopmentProject, MobileAppProject,
                      DataScienceProject extend Project
   - Encapsulation : private attributes with getters/setters
   - Polymorphism  : each subclass overrides calculate_billing()
                      and get_deliverables()
   - Composition   : Project "owns" a DevelopmentTracker and a Billing
                      object (they cannot exist without the project)
   - Aggregation   : Client "has" Projects, Company "has" Employees
   - Association   : Employee <-> Project through Assignment
=====================================================================
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Dict, Optional
import itertools

_id_counter = itertools.count(1)


def next_id(prefix: str) -> str:
    return f"{prefix}-{next(_id_counter):04d}"


# ---------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------
class ProjectStage(Enum):
    REQUIREMENT_FEASIBILITY = "Requirement Feasibility"
    TESTING = "Testing"
    DEPLOYMENT = "Deployment"
    MAINTENANCE = "Maintenance"


class ProjectStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"


class PaymentStatus(Enum):
    PENDING = "Pending"
    PARTIALLY_PAID = "Partially Paid"
    PAID = "Paid"


# ---------------------------------------------------------------
# EMPLOYEE
# ---------------------------------------------------------------
class Employee:
    """Represents a company employee who can be assigned to projects."""

    def __init__(self, name: str, designation: str, skills: List[str]):
        self._employee_id = next_id("EMP")
        self._name = name
        self._designation = designation
        self._skills = skills

    # ---- getters (encapsulation) ----
    @property
    def employee_id(self) -> str:
        return self._employee_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def designation(self) -> str:
        return self._designation

    @property
    def skills(self) -> List[str]:
        return self._skills

    def __str__(self):
        return f"{self._name} ({self._designation}) - Skills: {', '.join(self._skills)}"


# ---------------------------------------------------------------
# CLIENT
# ---------------------------------------------------------------
class Client:
    """Represents a client that owns one or more projects."""

    def __init__(self, name: str, contact_email: str, company_name: str):
        self._client_id = next_id("CLI")
        self._name = name
        self._contact_email = contact_email
        self._company_name = company_name
        self._projects: List["Project"] = []

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def name(self) -> str:
        return self._name

    def add_project(self, project: "Project"):
        self._projects.append(project)

    @property
    def projects(self) -> List["Project"]:
        return self._projects

    def __str__(self):
        return f"{self._name} ({self._company_name})"


# ---------------------------------------------------------------
# REQUIREMENT
# ---------------------------------------------------------------
class Requirement:
    """A single requirement/spec for a project."""

    def __init__(self, description: str, priority: str = "Medium"):
        self._requirement_id = next_id("REQ")
        self._description = description
        self._priority = priority
        self._is_fulfilled = False

    def mark_fulfilled(self):
        self._is_fulfilled = True

    def __str__(self):
        status = "Fulfilled" if self._is_fulfilled else "Pending"
        return f"[{self._priority}] {self._description} -> {status}"


# ---------------------------------------------------------------
# DEVELOPMENT TRACKER (Composition: lives & dies with its Project)
# ---------------------------------------------------------------
class DevelopmentTracker:
    """Tracks the life-cycle stage of a project."""

    STAGE_ORDER = [
        ProjectStage.REQUIREMENT_FEASIBILITY,
        ProjectStage.TESTING,
        ProjectStage.DEPLOYMENT,
        ProjectStage.MAINTENANCE,
    ]

    def __init__(self):
        self._current_index = 0
        self._history: List[Dict] = []
        self._log_stage_change(self.STAGE_ORDER[0])

    def _log_stage_change(self, stage: ProjectStage):
        self._history.append({"stage": stage, "timestamp": datetime.now()})

    @property
    def current_stage(self) -> ProjectStage:
        return self.STAGE_ORDER[self._current_index]

    def advance_stage(self) -> bool:
        """Move to the next life-cycle stage. Returns False if already at the end."""
        if self._current_index < len(self.STAGE_ORDER) - 1:
            self._current_index += 1
            self._log_stage_change(self.current_stage)
            return True
        return False

    @property
    def history(self):
        return self._history

    def __str__(self):
        return " -> ".join(
            f"{h['stage'].value}" + (" (current)" if h['stage'] == self.current_stage else "")
            for h in self._history
        )


# ---------------------------------------------------------------
# BILLING (Composition)
# ---------------------------------------------------------------
class Billing:
    """Handles invoicing/payment for a project."""

    def __init__(self, total_amount: float):
        self._billing_id = next_id("BILL")
        self._total_amount = total_amount
        self._amount_paid = 0.0
        self._status = PaymentStatus.PENDING
        self._invoice_date = date.today()

    def record_payment(self, amount: float):
        self._amount_paid += amount
        if self._amount_paid >= self._total_amount:
            self._status = PaymentStatus.PAID
        elif self._amount_paid > 0:
            self._status = PaymentStatus.PARTIALLY_PAID

    @property
    def balance_due(self) -> float:
        return round(self._total_amount - self._amount_paid, 2)

    @property
    def status(self) -> PaymentStatus:
        return self._status

    def generate_invoice(self) -> str:
        return (
            f"INVOICE {self._billing_id} | Date: {self._invoice_date} | "
            f"Total: Rs.{self._total_amount:.2f} | Paid: Rs.{self._amount_paid:.2f} | "
            f"Balance: Rs.{self.balance_due:.2f} | Status: {self._status.value}"
        )


# ---------------------------------------------------------------
# FEEDBACK
# ---------------------------------------------------------------
class Feedback:
    """Client feedback captured at a specific project stage."""

    def __init__(self, stage: ProjectStage, comments: str, rating: int):
        self._feedback_id = next_id("FB")
        self._stage = stage
        self._comments = comments
        self._rating = max(1, min(5, rating))
        self._timestamp = datetime.now()

    def __str__(self):
        return f"[{self._stage.value}] Rating: {self._rating}/5 - \"{self._comments}\""


# ---------------------------------------------------------------
# ASSIGNMENT (Association class between Employee & Project)
# ---------------------------------------------------------------
class Assignment:
    """Represents which employee handles which project, and in what role."""

    def __init__(self, employee: Employee, project: "Project", role: str):
        self._assignment_id = next_id("ASG")
        self._employee = employee
        self._project = project
        self._role = role
        self._assigned_date = date.today()

    @property
    def employee(self) -> Employee:
        return self._employee

    @property
    def role(self) -> str:
        return self._role

    def __str__(self):
        return f"{self._employee.name} assigned as '{self._role}' on {self._assigned_date}"


# ---------------------------------------------------------------
# PROJECT (Abstract Superclass)
# ---------------------------------------------------------------
class Project(ABC):
    """Abstract superclass for every kind of project the company runs."""

    def __init__(self, name: str, client: Client, budget: float, deadline: date):
        self._project_id = next_id("PRJ")
        self._name = name
        self._client = client
        self._budget = budget
        self._deadline = deadline
        self._status = ProjectStatus.NOT_STARTED
        self._requirements: List[Requirement] = []
        self._assignments: List[Assignment] = []
        self._feedbacks: List[Feedback] = []
        self._tracker = DevelopmentTracker()          # composition
        self._billing = Billing(total_amount=budget)   # composition
        client.add_project(self)

    # ---- shared behaviour ----
    def add_requirement(self, description: str, priority: str = "Medium"):
        self._requirements.append(Requirement(description, priority))

    def assign_employee(self, employee: Employee, role: str):
        assignment = Assignment(employee, self, role)
        self._assignments.append(assignment)
        return assignment

    def add_feedback(self, comments: str, rating: int):
        self._feedbacks.append(Feedback(self._tracker.current_stage, comments, rating))

    def advance_stage(self):
        moved = self._tracker.advance_stage()
        if self._tracker.current_stage == ProjectStage.MAINTENANCE:
            self._status = ProjectStatus.COMPLETED
        else:
            self._status = ProjectStatus.IN_PROGRESS
        return moved

    @property
    def project_id(self):
        return self._project_id

    @property
    def name(self):
        return self._name

    @property
    def billing(self) -> Billing:
        return self._billing

    @property
    def tracker(self) -> DevelopmentTracker:
        return self._tracker

    # ---- polymorphic / abstract behaviour ----
    @abstractmethod
    def calculate_billing(self) -> float:
        """Each project type may compute its final cost differently."""
        raise NotImplementedError

    @abstractmethod
    def get_deliverables(self) -> List[str]:
        raise NotImplementedError

    def generate_report(self) -> str:
        lines = [
            "=" * 70,
            f"PROJECT REPORT: {self._name}  [{self._project_id}]",
            "=" * 70,
            f"Type            : {self.__class__.__name__}",
            f"Client          : {self._client.name}",
            f"Status          : {self._status.value}",
            f"Deadline        : {self._deadline}",
            f"Life-cycle path : {self._tracker}",
            f"Deliverables    : {', '.join(self.get_deliverables())}",
            f"Requirements    :",
        ]
        for r in self._requirements:
            lines.append(f"   - {r}")
        lines.append("Team Assignments:")
        for a in self._assignments:
            lines.append(f"   - {a}")
        lines.append("Client Feedback:")
        for f in self._feedbacks:
            lines.append(f"   - {f}")
        lines.append(self._billing.generate_invoice())
        lines.append("=" * 70)
        return "\n".join(lines)


# ---------------------------------------------------------------
# CONCRETE SUBCLASSES (Inheritance + Polymorphism)
# ---------------------------------------------------------------
class WebDevelopmentProject(Project):
    def calculate_billing(self) -> float:
        # flat budget, no extra charges
        return self._budget

    def get_deliverables(self) -> List[str]:
        return ["Responsive Website", "Admin Dashboard", "Deployment on Cloud"]


class MobileAppProject(Project):
    def __init__(self, name, client, budget, deadline, platforms: List[str]):
        super().__init__(name, client, budget, deadline)
        self._platforms = platforms

    def calculate_billing(self) -> float:
        # extra 10% per additional platform beyond the first
        extra_platforms = max(0, len(self._platforms) - 1)
        return self._budget * (1 + 0.10 * extra_platforms)

    def get_deliverables(self) -> List[str]:
        return [f"{p} App Build" for p in self._platforms] + ["Play/App Store Listing"]


class DataScienceProject(Project):
    def __init__(self, name, client, budget, deadline, dataset_size_gb: float):
        super().__init__(name, client, budget, deadline)
        self._dataset_size_gb = dataset_size_gb

    def calculate_billing(self) -> float:
        # extra compute cost for large datasets
        compute_surcharge = 500 if self._dataset_size_gb > 50 else 0
        return self._budget + compute_surcharge

    def get_deliverables(self) -> List[str]:
        return ["Trained Model", "EDA Report", "Model Deployment API"]


# ---------------------------------------------------------------
# COMPANY (Top-level aggregate root)
# ---------------------------------------------------------------
class Company:
    """The company that manages everything: employees, clients, projects."""

    def __init__(self, name: str):
        self._name = name
        self._employees: List[Employee] = []
        self._clients: List[Client] = []
        self._projects: List[Project] = []

    def hire_employee(self, employee: Employee):
        self._employees.append(employee)

    def onboard_client(self, client: Client):
        self._clients.append(client)

    def register_project(self, project: Project):
        self._projects.append(project)

    @property
    def projects(self):
        return self._projects

    @property
    def employees(self):
        return self._employees

    def company_summary(self) -> str:
        lines = [
            f"COMPANY: {self._name}",
            f"Employees : {len(self._employees)}",
            f"Clients   : {len(self._clients)}",
            f"Projects  : {len(self._projects)}",
        ]
        return "\n".join(lines)
