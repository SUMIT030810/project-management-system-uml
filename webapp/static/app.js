/* =====================================================================
   BrightWave Project Control — frontend logic
   Plain vanilla JS. Every function either (a) asks the Flask API for
   data with fetch(), or (b) renders that data into the page.
===================================================================== */

const STAGES = ["Requirement Feasibility", "Testing", "Deployment", "Maintenance"];

let state = {
  employees: [],
  clients: [],
  projects: [],
  currentProjectId: null,
};

// ---------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

function showToast(message, isError = false) {
  const t = document.getElementById("toast");
  t.textContent = message;
  t.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => (t.className = "toast"), 2600);
}

function money(n) {
  return "Rs. " + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function statusBadge(status) {
  const map = {
    "Completed": "badge-completed",
    "In Progress": "badge-progress",
    "Not Started": "badge-pending",
    "On Hold": "badge-pending",
  };
  return `<span class="badge ${map[status] || "badge-pending"}">${status}</span>`;
}

// ---------------------------------------------------------------
// Navigation between views
// ---------------------------------------------------------------
function showView(viewId) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(viewId).classList.add("active");
  document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
  const navBtn = document.querySelector(`.nav-item[data-view="${viewId.replace('view-', '')}"]`);
  if (navBtn) navBtn.classList.add("active");
}

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    const target = "view-" + btn.dataset.view;
    showView(target);
    if (btn.dataset.view === "dashboard") loadDashboard();
    if (btn.dataset.view === "projects") loadProjectsList();
    if (btn.dataset.view === "employees") loadEmployeesTable();
    if (btn.dataset.view === "clients") loadClientsTable();
  });
});

document.getElementById("back-to-projects").addEventListener("click", () => {
  showView("view-projects");
  loadProjectsList();
});

// ---------------------------------------------------------------
// DASHBOARD
// ---------------------------------------------------------------
async function loadDashboard() {
  const summary = await api("/api/summary");
  const grid = document.getElementById("stat-grid");
  grid.innerHTML = [
    ["Employees", summary.employees],
    ["Clients", summary.clients],
    ["Projects", summary.projects],
    ["Total billed", money(summary.total_billed)],
    ["Outstanding", money(summary.total_outstanding)],
  ].map(([label, value]) => `
    <div class="stat-card">
      <div class="stat-value">${value}</div>
      <div class="stat-label">${label}</div>
    </div>`).join("");

  state.projects = await api("/api/projects");
  renderProjectList("dashboard-project-list", state.projects);
}

function renderProjectList(containerId, projects) {
  const el = document.getElementById(containerId);
  if (!projects.length) {
    el.innerHTML = `<div class="empty-note">No projects yet — create one to get started.</div>`;
    return;
  }
  el.innerHTML = projects.map(p => `
    <div class="project-card" data-id="${p.id}">
      <div class="pc-left">
        <div class="pc-name">${p.name}</div>
        <div class="pc-sub">${p.id} · ${p.client} · ${p.type}</div>
      </div>
      <div class="pc-right">
        <span class="badge badge-progress">${p.current_stage}</span>
        ${statusBadge(p.status)}
      </div>
    </div>`).join("");
  el.querySelectorAll(".project-card").forEach(card => {
    card.addEventListener("click", () => openProjectDetail(card.dataset.id));
  });
}

// ---------------------------------------------------------------
// PROJECTS LIST VIEW
// ---------------------------------------------------------------
async function loadProjectsList() {
  state.projects = await api("/api/projects");
  renderProjectList("projects-list", state.projects);
}

// ---------------------------------------------------------------
// PROJECT DETAIL VIEW
// ---------------------------------------------------------------
async function openProjectDetail(projectId) {
  state.currentProjectId = projectId;
  showView("view-project-detail");
  await refreshProjectDetail();
}

async function refreshProjectDetail() {
  const p = await api(`/api/projects/${state.currentProjectId}`);

  document.getElementById("pd-type").textContent = p.type;
  document.getElementById("pd-name").textContent = p.name;
  document.getElementById("pd-meta").textContent =
    `${p.id} · Client: ${p.client} · Deadline: ${p.deadline} · Budget: ${money(p.budget)}`;

  // Lifecycle rail
  const currentIdx = STAGES.indexOf(p.current_stage);
  const rail = document.getElementById("lifecycle-rail");
  rail.innerHTML = STAGES.map((stage, i) => {
    let cls = "";
    if (i < currentIdx) cls = "done";
    else if (i === currentIdx) cls = "current";
    return `
      <div class="rail-step ${cls}">
        <div class="rail-connector"></div>
        <div class="rail-node">${i + 1}</div>
        <div class="rail-label">${stage}</div>
      </div>`;
  }).join("");

  const advanceBtn = document.getElementById("btn-advance-stage");
  advanceBtn.disabled = currentIdx === STAGES.length - 1;
  advanceBtn.textContent = currentIdx === STAGES.length - 1 ? "Life-cycle complete" : "Advance stage \u2192";

  // Assignments
  const asg = document.getElementById("pd-assignments");
  asg.innerHTML = p.assignments.length
    ? p.assignments.map(a => `
        <li><div class="li-title">${a.employee}</div><div class="li-sub">${a.role} · assigned ${a.date}</div></li>
      `).join("")
    : `<li class="empty-note">No one assigned yet.</li>`;

  // Requirements
  const req = document.getElementById("pd-requirements");
  req.innerHTML = p.requirements.length
    ? p.requirements.map(r => `
        <li><div class="li-title">${r.description}</div><div class="li-sub">Priority: ${r.priority}</div></li>
      `).join("")
    : `<li class="empty-note">No requirements logged yet.</li>`;

  // Billing
  document.getElementById("pd-billing").innerHTML = `
    <div class="b-row"><span>Final billing amount</span><span class="b-amount">${money(p.final_billing)}</span></div>
    <div class="b-row"><span>Balance due</span><span class="b-amount">${money(p.balance_due)}</span></div>
    <div class="b-row"><span>Status</span>${statusBadge(p.payment_status === 'Paid' ? 'Completed' : 'Not Started')}</div>
  `;

  // Feedback
  const fb = document.getElementById("pd-feedback");
  fb.innerHTML = p.feedbacks.length
    ? p.feedbacks.map(f => `
        <li><div class="li-title">${"\u2605".repeat(f.rating)}${"\u2606".repeat(5 - f.rating)} — ${f.stage}</div><div class="li-sub">"${f.comments}"</div></li>
      `).join("")
    : `<li class="empty-note">No feedback logged yet.</li>`;
}

document.getElementById("btn-advance-stage").addEventListener("click", async () => {
  try {
    await api(`/api/projects/${state.currentProjectId}/advance`, { method: "POST" });
    showToast("Project moved to the next stage");
    refreshProjectDetail();
  } catch (e) { showToast(e.message, true); }
});

// ---------------------------------------------------------------
// EMPLOYEES / CLIENTS TABLES
// ---------------------------------------------------------------
async function loadEmployeesTable() {
  state.employees = await api("/api/employees");
  const tbody = document.querySelector("#employees-table tbody");
  tbody.innerHTML = state.employees.map(e => `
    <tr><td>${e.id}</td><td>${e.name}</td><td>${e.designation}</td><td>${e.skills.join(", ")}</td></tr>
  `).join("") || `<tr><td colspan="4" class="empty-note">No employees yet.</td></tr>`;
}

async function loadClientsTable() {
  state.clients = await api("/api/clients");
  const tbody = document.querySelector("#clients-table tbody");
  tbody.innerHTML = state.clients.map(c => `
    <tr><td>${c.id}</td><td>${c.name}</td><td>${c.company_name || ""}</td><td>${c.project_count}</td></tr>
  `).join("") || `<tr><td colspan="4" class="empty-note">No clients yet.</td></tr>`;
}

// ---------------------------------------------------------------
// MODALS
// ---------------------------------------------------------------
const backdrop = document.getElementById("modal-backdrop");

async function openModal(name) {
  document.querySelectorAll(".modal").forEach(m => m.classList.remove("open"));
  const modal = document.querySelector(`.modal[data-modal="${name}"]`);
  modal.classList.add("open");
  backdrop.classList.add("open");

  if (name === "new-project") {
    state.clients = await api("/api/clients");
    const select = document.getElementById("select-client");
    select.innerHTML = state.clients.map(c => `<option value="${c.id}">${c.name} (${c.company_name || c.name})</option>`).join("")
      || `<option value="">No clients yet — add one first</option>`;
  }
  if (name === "assign-employee") {
    state.employees = await api("/api/employees");
    const select = document.getElementById("select-assign-employee");
    select.innerHTML = state.employees.map(e => `<option value="${e.id}">${e.name} — ${e.designation}</option>`).join("")
      || `<option value="">No employees yet — add one first</option>`;
  }
}

function closeModals() {
  document.querySelectorAll(".modal").forEach(m => m.classList.remove("open"));
  backdrop.classList.remove("open");
}

document.querySelectorAll("[data-open-modal]").forEach(btn => {
  btn.addEventListener("click", () => openModal(btn.dataset.openModal));
});
document.querySelectorAll("[data-close-modal]").forEach(btn => {
  btn.addEventListener("click", closeModals);
});
backdrop.addEventListener("click", (e) => { if (e.target === backdrop) closeModals(); });

// Conditional fields in the "new project" form
document.getElementById("select-type").addEventListener("change", (e) => {
  document.getElementById("field-platforms").style.display = e.target.value === "mobile" ? "flex" : "none";
  document.getElementById("field-dataset").style.display = e.target.value === "data" ? "flex" : "none";
});

// ---------------------------------------------------------------
// FORM SUBMISSIONS
// ---------------------------------------------------------------
document.getElementById("modal-new-employee").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await api("/api/employees", { method: "POST", body: JSON.stringify(Object.fromEntries(fd)) });
    showToast("Employee added");
    closeModals(); e.target.reset();
    loadEmployeesTable(); loadDashboard();
  } catch (err) { showToast(err.message, true); }
});

document.getElementById("modal-new-client").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await api("/api/clients", { method: "POST", body: JSON.stringify(Object.fromEntries(fd)) });
    showToast("Client added");
    closeModals(); e.target.reset();
    loadClientsTable(); loadDashboard();
  } catch (err) { showToast(err.message, true); }
});

document.getElementById("modal-new-project").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    await api("/api/projects", { method: "POST", body: JSON.stringify(fd) });
    showToast("Project created");
    closeModals(); e.target.reset();
    loadProjectsList(); loadDashboard();
  } catch (err) { showToast(err.message, true); }
});

document.getElementById("modal-assign-employee").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    await api(`/api/projects/${state.currentProjectId}/assign`, { method: "POST", body: JSON.stringify(fd) });
    showToast("Employee assigned");
    closeModals(); e.target.reset();
    refreshProjectDetail();
  } catch (err) { showToast(err.message, true); }
});

document.getElementById("modal-add-requirement").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    await api(`/api/projects/${state.currentProjectId}/requirements`, { method: "POST", body: JSON.stringify(fd) });
    showToast("Requirement added");
    closeModals(); e.target.reset();
    refreshProjectDetail();
  } catch (err) { showToast(err.message, true); }
});

document.getElementById("modal-record-payment").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    await api(`/api/projects/${state.currentProjectId}/payment`, { method: "POST", body: JSON.stringify(fd) });
    showToast("Payment recorded");
    closeModals(); e.target.reset();
    refreshProjectDetail();
  } catch (err) { showToast(err.message, true); }
});

document.getElementById("modal-add-feedback").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    await api(`/api/projects/${state.currentProjectId}/feedback`, { method: "POST", body: JSON.stringify(fd) });
    showToast("Feedback added");
    closeModals(); e.target.reset();
    refreshProjectDetail();
  } catch (err) { showToast(err.message, true); }
});

// ---------------------------------------------------------------
// INIT
// ---------------------------------------------------------------
loadDashboard();
