const namespaceSelect = document.getElementById("namespace-select");
const namespaceSearch = document.getElementById("namespace-search");
const podsTableBody = document.querySelector("#pods-table tbody");
const podsCount = document.getElementById("pods-count");
const cpuUsageLabel = document.getElementById("cpu-usage");
const memoryUsageLabel = document.getElementById("memory-usage");
const cpuProgress = document.getElementById("cpu-progress");
const memoryProgress = document.getElementById("memory-progress");
const appNameField = document.getElementById("app-name");
const microservicesField = document.getElementById("microservices");
const repoUrlField = document.getElementById("repo-url");
const techStackField = document.getElementById("tech-stack");
const roadmapStatusField = document.getElementById("roadmap-status");
const migrationProgressField = document.getElementById("migration-progress");
const ownershipField = document.getElementById("ownership");
const hostingLocationField = document.getElementById("hosting-location");
const labelDxId = document.getElementById("label-dx-id");
const labelDxEnvironment = document.getElementById("label-dx-environment");
const labelDxIsProduction = document.getElementById("label-dx-is-production");
const messageBanner = document.getElementById("message-banner");

let namespaces = [];

function showMessage(message, type = "info") {
    messageBanner.textContent = message;
    messageBanner.className = `message-banner ${type}`;
    messageBanner.classList.remove("hidden");
}

function hideMessage() {
    messageBanner.classList.add("hidden");
}

function buildPodRows(pods, metrics) {
    const metricLookup = {};
    metrics.forEach((item) => {
        metricLookup[item.pod_name] = item;
    });

    return pods.map((pod) => {
        const metric = metricLookup[pod.name] || { containers: [] };
        const containerInfo = metric.containers.length
            ? metric.containers
                  .map((container) => `${container.name}: ${container.cpu || "-"} / ${container.memory || "-"}`)
                  .join("<br />")
            : pod.container_statuses
                  .map((container) => `${container.name}: ${container.state ? JSON.stringify(container.state) : "-"}`)
                  .join("<br />");

        return `
            <tr>
                <td>${pod.name}</td>
                <td>${pod.status}</td>
                <td>${containerInfo || "-"}</td>
            </tr>
        `;
    }).join("");
}

function renderResourceBars(totalCpu, totalMemory) {
    const cpuValue = totalCpu || "-";
    const memoryValue = totalMemory || "-";
    cpuUsageLabel.textContent = cpuValue;
    memoryUsageLabel.textContent = memoryValue;

    const cpuProgressValue = parseResourceNumber(totalCpu);
    const memoryProgressValue = parseResourceNumber(totalMemory);

    cpuProgress.style.width = `${Math.min(cpuProgressValue, 100)}%`;
    memoryProgress.style.width = `${Math.min(memoryProgressValue, 100)}%`;
    cpuProgress.dataset.level = cpuProgressValue;
    memoryProgress.dataset.level = memoryProgressValue;
}

function parseResourceNumber(value) {
    if (!value) return 0;
    const number = parseFloat(value.replace(/[a-zA-Z%]+/g, ""));
    return Number.isNaN(number) ? 0 : Math.min(number, 100);
}

function setGovernanceLabel(element, valid) {
    element.textContent = valid ? "✓" : "✕";
    element.classList.toggle("pass", valid);
    element.classList.toggle("fail", !valid);
}

function updateAppInfo(data) {
    appNameField.textContent = data.application_name || "-";
    microservicesField.textContent = data.microservices?.length ? data.microservices.join(", ") : "-";
    repoUrlField.textContent = data.repo_url || "-";
    repoUrlField.href = data.repo_url || "#";
    techStackField.textContent = data.tech_stack || "-";

    roadmapStatusField.textContent = data.migration_status?.roadmap_status || "-";
    migrationProgressField.textContent = data.migration_status?.migration_progress || "-";
    ownershipField.textContent = data.migration_status?.ownership || "-";
    hostingLocationField.textContent = data.migration_status?.hosting_location || "-";

    setGovernanceLabel(labelDxId, data.governance_labels?.["dx-id"] === true);
    setGovernanceLabel(labelDxEnvironment, data.governance_labels?.["dx-environment"] === true);
    setGovernanceLabel(labelDxIsProduction, data.governance_labels?.["dx-is-production"] === true);
}

function renderNamespaceDetail(data) {
    hideMessage();
    const pods = data.pods || [];
    podsCount.textContent = pods.length;
    podsTableBody.innerHTML = buildPodRows(pods, data.resource_usage || []);
    renderResourceBars(data.cpu, data.memory);
    updateAppInfo(data);
}

async function fetchNamespaces() {
    try {
        const response = await fetch("/api/namespaces");
        if (!response.ok) throw new Error(`Failed to load namespaces (${response.status})`);
        namespaces = await response.json();
        populateNamespaceSelector(namespaces);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function populateNamespaceSelector(list) {
    namespaceSelect.innerHTML = "<option value=\"\">Select a namespace...</option>";
    list.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.name;
        option.textContent = item.name;
        namespaceSelect.appendChild(option);
    });
}

async function fetchNamespaceDetail(name) {
    if (!name) return;
    try {
        showMessage("Loading namespace data...", "info");
        const response = await fetch(`/api/namespace/${encodeURIComponent(name)}`);
        if (!response.ok) {
            const payload = await response.json().catch(() => null);
            const message = payload?.detail || `Failed to load namespace data (${response.status})`;
            throw new Error(message);
        }
        const data = await response.json();
        renderNamespaceDetail(data);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

namespaceSelect.addEventListener("change", (event) => {
    const selected = event.target.value;
    if (selected) fetchNamespaceDetail(selected);
});

namespaceSearch.addEventListener("input", (event) => {
    const query = event.target.value.trim().toLowerCase();
    const filtered = namespaces.filter((item) => item.name.toLowerCase().includes(query));
    populateNamespaceSelector(filtered);
});

window.addEventListener("DOMContentLoaded", () => {
    fetchNamespaces();
});
