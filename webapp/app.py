"""
=====================================================================
 FLASK BACKEND — Project Management System Web Interface
=====================================================================
 This file exposes the existing OOP system (src/pms.py) as a REST
 API so a browser-based frontend (webapp/templates/index.html) can
 create employees/clients/projects, assign staff, advance the
 project life-cycle, record billing, and leave feedback — all
 without touching Python directly.

 Data lives in memory (a single Company object) for simplicity.
 Restarting the server resets all data. See the guide for how to
 add persistence (SQLite) later.
=====================================================================
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import date, datetime
from flask import Flask, jsonify, request, render_template

from pms import (
    Company, Employee, Client,
    WebDevelopmentProject, MobileAppProject, DataScienceProject,
    ProjectStage, ProjectStatus, PaymentStatus,
)

app = Flask(__name__)

# ---------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------
company = Company("BrightWave Technologies")

PROJECT_TYPES = {
    "web": WebDevelopmentProject,
    "mobile": MobileAppProject,
    "data": DataScienceProject,
}


# ---------------------------------------------------------------
# Serialization helpers (turn Python objects into JSON-friendly dicts)
# ---------------------------------------------------------------
def employee_to_dict(e: Employee):
    return {
        "id": e.employee_id,
        "name": e.name,
        "designation": e.designation,
        "skills": e.skills,
    }


def client_to_dict(c: Client):
    return {
        "id": c.client_id,
        "name": c.name,
        "company_name": c._company_name,
        "project_count": len(c.projects),
    }


def project_to_dict(p, detailed=False):
    base = {
        "id": p.project_id,
        "name": p.name,
        "type": p.__class__.__name__,
        "client": p._client.name,
        "client_id": p._client.client_id,
        "status": p._status.value,
        "deadline": str(p._deadline),
        "current_stage": p.tracker.current_stage.value,
        "budget": p._budget,
        "final_billing": p.calculate_billing(),
        "balance_due": p.billing.balance_due,
        "payment_status": p.billing.status.value,
        "deliverables": p.get_deliverables(),
    }
    if detailed:
        base["requirements"] = [
            {"id": r._requirement_id, "description": r._description,
             "priority": r._priority, "fulfilled": r._is_fulfilled}
            for r in p._requirements
        ]
        base["assignments"] = [
            {"employee": a.employee.name, "employee_id": a.employee.employee_id,
             "role": a.role, "date": str(a._assigned_date)}
            for a in p._assignments
        ]
        base["feedbacks"] = [
            {"stage": f._stage.value, "comments": f._comments, "rating": f._rating,
             "timestamp": f._timestamp.strftime("%Y-%m-%d %H:%M")}
            for f in p._feedbacks
        ]
        base["stage_history"] = [h["stage"].value for h in p.tracker.history]
        base["invoice"] = p.billing.generate_invoice()
    return base


# ---------------------------------------------------------------
# Page route (serves the single-page frontend)
# ---------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------
# EMPLOYEES
# ---------------------------------------------------------------
@app.route("/api/employees", methods=["GET"])
def list_employees():
    return jsonify([employee_to_dict(e) for e in company.employees])


@app.route("/api/employees", methods=["POST"])
def create_employee():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    designation = (data.get("designation") or "").strip()
    skills = [s.strip() for s in (data.get("skills") or "").split(",") if s.strip()]
    if not name or not designation:
        return jsonify({"error": "name and designation are required"}), 400
    emp = Employee(name, designation, skills)
    company.hire_employee(emp)
    return jsonify(employee_to_dict(emp)), 201


# ---------------------------------------------------------------
# CLIENTS
# ---------------------------------------------------------------
@app.route("/api/clients", methods=["GET"])
def list_clients():
    return jsonify([client_to_dict(c) for c in company._clients])


@app.route("/api/clients", methods=["POST"])
def create_client():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    company_name = (data.get("company_name") or "").strip()
    if not name or not company_name:
        return jsonify({"error": "name and company_name are required"}), 400
    client = Client(name, email, company_name)
    company.onboard_client(client)
    return jsonify(client_to_dict(client)), 201


def find_client(client_id):
    return next((c for c in company._clients if c.client_id == client_id), None)


def find_employee(employee_id):
    return next((e for e in company.employees if e.employee_id == employee_id), None)


def find_project(project_id):
    return next((p for p in company.projects if p.project_id == project_id), None)


# ---------------------------------------------------------------
# PROJECTS
# ---------------------------------------------------------------
@app.route("/api/projects", methods=["GET"])
def list_projects():
    return jsonify([project_to_dict(p) for p in company.projects])


@app.route("/api/projects", methods=["POST"])
def create_project():
    data = request.get_json(force=True)
    ptype = data.get("type")
    name = (data.get("name") or "").strip()
    client_id = data.get("client_id")
    budget = data.get("budget")
    deadline_str = data.get("deadline")

    if ptype not in PROJECT_TYPES:
        return jsonify({"error": f"type must be one of {list(PROJECT_TYPES)}"}), 400
    client = find_client(client_id)
    if not client:
        return jsonify({"error": "client not found"}), 404
    if not name or not budget or not deadline_str:
        return jsonify({"error": "name, budget and deadline are required"}), 400

    try:
        budget = float(budget)
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify({"error": "invalid budget or deadline format (use YYYY-MM-DD)"}), 400

    cls = PROJECT_TYPES[ptype]
    if ptype == "mobile":
        platforms = [p.strip() for p in (data.get("platforms") or "Android,iOS").split(",") if p.strip()]
        project = cls(name, client, budget, deadline, platforms=platforms)
    elif ptype == "data":
        dataset_size_gb = float(data.get("dataset_size_gb") or 0)
        project = cls(name, client, budget, deadline, dataset_size_gb=dataset_size_gb)
    else:
        project = cls(name, client, budget, deadline)

    company.register_project(project)
    return jsonify(project_to_dict(project)), 201


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    project = find_project(project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    return jsonify(project_to_dict(project, detailed=True))


@app.route("/api/projects/<project_id>/requirements", methods=["POST"])
def add_requirement(project_id):
    project = find_project(project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    data = request.get_json(force=True)
    description = (data.get("description") or "").strip()
    priority = data.get("priority") or "Medium"
    if not description:
        return jsonify({"error": "description is required"}), 400
    project.add_requirement(description, priority)
    return jsonify(project_to_dict(project, detailed=True)), 201


@app.route("/api/projects/<project_id>/assign", methods=["POST"])
def assign_employee(project_id):
    project = find_project(project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    data = request.get_json(force=True)
    employee = find_employee(data.get("employee_id"))
    role = (data.get("role") or "").strip()
    if not employee or not role:
        return jsonify({"error": "valid employee_id and role are required"}), 400
    project.assign_employee(employee, role)
    return jsonify(project_to_dict(project, detailed=True)), 201


@app.route("/api/projects/<project_id>/advance", methods=["POST"])
def advance_stage(project_id):
    project = find_project(project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    moved = project.advance_stage()
    if not moved:
        return jsonify({"error": "project is already at the final stage (Maintenance)"}), 400
    return jsonify(project_to_dict(project, detailed=True))


@app.route("/api/projects/<project_id>/feedback", methods=["POST"])
def add_feedback(project_id):
    project = find_project(project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    data = request.get_json(force=True)
    comments = (data.get("comments") or "").strip()
    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "rating must be an integer 1-5"}), 400
    if not comments:
        return jsonify({"error": "comments are required"}), 400
    project.add_feedback(comments, rating)
    return jsonify(project_to_dict(project, detailed=True)), 201


@app.route("/api/projects/<project_id>/payment", methods=["POST"])
def record_payment(project_id):
    project = find_project(project_id)
    if not project:
        return jsonify({"error": "project not found"}), 404
    data = request.get_json(force=True)
    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400
    project.billing.record_payment(amount)
    return jsonify(project_to_dict(project, detailed=True))


# ---------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------
@app.route("/api/summary", methods=["GET"])
def summary():
    return jsonify({
        "company_name": company._name,
        "employees": len(company.employees),
        "clients": len(company._clients),
        "projects": len(company.projects),
        "in_progress": sum(1 for p in company.projects if p._status == ProjectStatus.IN_PROGRESS),
        "completed": sum(1 for p in company.projects if p._status == ProjectStatus.COMPLETED),
        "total_billed": round(sum(p.calculate_billing() for p in company.projects), 2),
        "total_outstanding": round(sum(p.billing.balance_due for p in company.projects), 2),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
