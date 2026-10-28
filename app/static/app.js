const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
let projects = [];

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || response.statusText);
  }
  return response.json();
}

function switchView(id) {
  $$(".view").forEach((view) => view.classList.toggle("active", view.id === id));
  $$(".nav").forEach((item) => item.classList.toggle("active", item.dataset.view === id));
}

$$(".nav").forEach((item) => {
  item.onclick = () => switchView(item.dataset.view);
});
$("#commandButton").onclick = () => {
  switchView("home");
  $("#chatInput").focus();
};

async function loadProjects() {
  projects = await api("/api/projects");
  $("#projects").innerHTML = projects
    .map((project) => `<article><p class="eyebrow">PROJECT ${project.id}</p><h3>${escapeHtml(project.name)}</h3><p>${escapeHtml(project.description)}</p><small>${project.created_at}</small></article>`)
    .join("");
  $("#uploadProject").innerHTML = '<option value="">No project</option>' +
    projects.map((project) => `<option value="${project.id}">${escapeHtml(project.name)}</option>`).join("");
  const projectOptions = projects
    .map((project) => `<option value="${project.id}">${escapeHtml(project.name)}</option>`)
    .join("");
  $("#chatScope").innerHTML = '<option value="">All projects</option>' + projectOptions;
  $("#memoryScope").innerHTML = '<option value="">Global</option>' + projectOptions;
}

async function loadAgents() {
  const agents = await api("/api/agents");
  $("#agentsGrid").innerHTML = agents
    .map((agent) => `<article><div class="agent-status">● ${escapeHtml(agent.status)}</div><h3>${escapeHtml(agent.name)}</h3><p>${escapeHtml(agent.role)}</p><small>${escapeHtml(agent.id)}</small></article>`)
    .join("");
}

async function loadMemory() {
  const rows = await api("/api/memory");
  $("#memoryList").innerHTML = rows.length
    ? rows.map((memory) => `<div class="result"><strong>${escapeHtml(memory.kind)}</strong><p>${escapeHtml(memory.content)}</p><small>Project ${memory.project_id ?? "global"} · ${escapeHtml(memory.created_at)}</small></div>`).join("")
    : "<p>No stored memory yet.</p>";
}

$("#newProject").onclick = async () => {
  const name = prompt("Project name");
  if (!name) return;
  const description = prompt("Project description") || "";
  await api("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
  await loadProjects();
};

$("#addMemory").onclick = async () => {
  const content = prompt("Memory to store");
  if (!content) return;
  const project_id = $("#memoryScope").value ? Number($("#memoryScope").value) : null;
  await api("/api/memory", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_id, kind: "project", content }),
  });
  await loadMemory();
};

$("#uploadFile").onclick = async () => {
  const file = $("#fileInput").files[0];
  if (!file) {
    alert("Choose a UTF-8 text file.");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  if ($("#uploadProject").value) formData.append("project_id", $("#uploadProject").value);
  $("#uploadStatus").textContent = "Indexing…";
  try {
    const result = await api("/api/documents", { method: "POST", body: formData });
    $("#uploadStatus").textContent = `Indexed ${result.name}`;
  } catch (error) {
    $("#uploadStatus").textContent = error.message;
  }
};

$("#runSearch").onclick = async () => {
  const query = $("#searchInput").value.trim();
  if (!query) return;
  try {
    const rows = await api("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, limit: 20 }),
    });
    $("#searchResults").innerHTML = rows.length
      ? rows.map((row) => `<div class="result"><strong>${escapeHtml(row.name)}</strong><p>${safeSnippet(row.snippet)}</p><small>Project ${row.project_id ?? "global"}</small></div>`).join("")
      : "<p>No evidence found.</p>";
  } catch (error) {
    $("#searchResults").textContent = error.message;
  }
};

$("#sendChat").onclick = async () => {
  const message = $("#chatInput").value.trim();
  if (!message) return;
  $("#chatOutput").textContent = "Planning and routing…";
  try {
    const result = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        project_id: $("#chatScope").value ? Number($("#chatScope").value) : null,
        mode: "auto",
      }),
    });
    $("#chatOutput").textContent = `${result.answer}\n\nRoute: ${result.route.mode}\nAgents: ${result.route.agents.join(", ")}\nProvider: ${result.route.provider}`;
  } catch (error) {
    $("#chatOutput").textContent = error.message;
  }
};

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  })[character]);
}

function safeSnippet(value = "") {
  return escapeHtml(value)
    .replaceAll("&lt;mark&gt;", "<mark>")
    .replaceAll("&lt;/mark&gt;", "</mark>");
}

Promise.all([loadProjects(), loadAgents(), loadMemory()]).catch((error) => {
  $("#chatOutput").textContent = `Unable to load Onoma: ${error.message}`;
});
