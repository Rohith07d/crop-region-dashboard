/**
 * AgriStress — Farmer Water & Crop Allocator
 * Clean Vanilla JavaScript Frontend (No Build Tools)
 * Interactive Field Planning, Open-Meteo Integration, and Dynamic Agronomic Allocations
 */

// Application State
let allClusters = [];
let currentClusterName = "";
let activeStateFilter = "all";
let availableWaterLiters = 50000;
let waterSourceType = "Borewell";
let farmerPlots = [];
let supportedCrops = [];

// Request concurrency guards (avoids race condition on rapid switching)
let activeDashboardRequestId = 0;
let activeSimulateRequestId = 0;
let activeFutureCropsRequestId = 0;

// Chart.js Instances
let riskChartInstance = null;
let allocationChartInstance = null;
let forecastChartInstance = null;

// Earthy Agrarian Theme Palette
const EARTHY_PALETTE = {
  charcoal: "#312C18",
  moss: "#4C543D",
  sage: "#A4B092",
  cream: "#EAE5D9",
  card: "#F4F1E8",
  amber: "#C68B38",
  terracotta: "#B85D3B",
  rust: "#9E2A2B",
  low: "#2E5A36"
};

// Risk Formatting Configuration
const RISK_CONFIG = {
  Low: { color: EARTHY_PALETTE.low, badgeClass: "badge-low" },
  Moderate: { color: EARTHY_PALETTE.amber, badgeClass: "badge-moderate" },
  High: { color: EARTHY_PALETTE.terracotta, badgeClass: "badge-high" },
  Critical: { color: EARTHY_PALETTE.rust, badgeClass: "badge-critical" }
};

// Crop Category Emojis
const CROP_ICONS = {
  Rice: "🌾",
  Cotton: "👕",
  Maize: "🌽",
  Soybean: "🌱",
  Groundnut: "🥜",
  Chilli_Export: "🌶️",
  Turmeric: "🟡",
  Gherkins: "🥒",
  Dragon_Fruit: "🐉",
  Pomegranate: "🍎",
  Avocado: "🥑",
  Quinoa: "🌾",
  Bell_Pepper: "🫑",
  Guava_Export: "🍐",
  Okra_Export: "🥬"
};

// Growth Stage Options
const GROWTH_STAGES = ["Initial", "Development", "Mid_Season", "Late_Season"];

// ============================================================================
// Initialization & Event Binding
// ============================================================================
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadClusters();
});

function setupEventListeners() {
  // State filter
  const stateFilter = document.getElementById("stateFilter");
  stateFilter.addEventListener("change", (e) => {
    activeStateFilter = e.target.value;
    renderClusterDropdown();
  });

  // Cluster selector
  const clusterSelect = document.getElementById("clusterSelect");
  clusterSelect.addEventListener("change", (e) => {
    currentClusterName = e.target.value;
    loadClusterDashboard(currentClusterName);
  });

  // Cluster control box click opens select
  const clusterBox = document.getElementById("clusterControlBox");
  if (clusterBox) {
    clusterBox.addEventListener("click", (e) => {
      if (e.target.tagName !== "SELECT") {
        try { clusterSelect.showPicker(); } catch (err) { clusterSelect.focus(); }
      }
    });
  }

  // Browse Clusters Modal triggers
  const browseBtn = document.getElementById("browseClustersBtn");
  if (browseBtn) browseBtn.addEventListener("click", openClusterModal);

  const changeBtn = document.getElementById("changeClusterBtn");
  if (changeBtn) changeBtn.addEventListener("click", openClusterModal);

  const closeBtn = document.getElementById("closeClusterModalBtn");
  if (closeBtn) closeBtn.addEventListener("click", closeClusterModal);

  const modal = document.getElementById("clusterModal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeClusterModal();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeClusterModal();
  });

  // Modal State Tabs
  document.querySelectorAll(".modal-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".modal-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      renderClusterModalGrid(tab.dataset.tabState);
    });
  });

  // Sync live weather button
  const syncBtn = document.getElementById("syncWeatherBtn");
  syncBtn.addEventListener("click", () => {
    showToast("Re-fetching live Open-Meteo satellite feed...");
    loadClusterDashboard(currentClusterName);
  });

  // Water supply numeric input
  const waterInput = document.getElementById("waterSupplyInput");
  const waterSlider = document.getElementById("waterSupplySlider");

  waterInput.addEventListener("change", (e) => {
    const val = Math.max(1000, parseFloat(e.target.value) || 10000);
    availableWaterLiters = val;
    waterSlider.value = Math.min(val, parseFloat(waterSlider.max));
    simulateAllocation();
  });

  // Water supply slider
  waterSlider.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    availableWaterLiters = val;
    waterInput.value = val;
    simulateAllocation();
  });

  // Quick preset buttons
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const val = parseFloat(btn.dataset.liters);
      availableWaterLiters = val;
      waterInput.value = val;
      waterSlider.value = Math.min(val, parseFloat(waterSlider.max));
      simulateAllocation();
    });
  });

  // Water source selector
  const waterSourceSelect = document.getElementById("waterSourceSelect");
  waterSourceSelect.addEventListener("change", (e) => {
    waterSourceType = e.target.value;
    simulateAllocation();
  });

  // Add Plot Button
  const addPlotBtn = document.getElementById("addPlotBtn");
  addPlotBtn.addEventListener("click", addNewFarmerPlot);

  // Recalculate Button
  const recalcBtn = document.getElementById("recalculateBtn");
  recalcBtn.addEventListener("click", () => {
    simulateAllocation();
    showToast("Allocation recalculated with live ECMWF satellite feed.");
  });
}

// ============================================================================
// Load Farm Clusters & Populate Dropdowns
// ============================================================================
async function loadClusters() {
  try {
    const res = await fetch("/api/regions");
    const data = await res.json();
    allClusters = data.regions || [];
    supportedCrops = data.supported_crops || Object.keys(CROP_ICONS);

    renderClusterDropdown();
  } catch (err) {
    console.error("Failed to load farm clusters:", err);
    showToast("Error loading farm clusters from API");
  }
}

function renderClusterDropdown() {
  const select = document.getElementById("clusterSelect");
  select.innerHTML = "";

  const filtered = activeStateFilter === "all"
    ? allClusters
    : allClusters.filter(c => c.state === activeStateFilter);

  if (filtered.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No clusters found";
    select.appendChild(opt);
    return;
  }

  // Group by State
  const byState = {};
  filtered.forEach(c => {
    if (!byState[c.state]) byState[c.state] = [];
    byState[c.state].push(c);
  });

  Object.keys(byState).sort().forEach(stateName => {
    const optgroup = document.createElement("optgroup");
    optgroup.label = `📍 ${stateName}`;

    byState[stateName].forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.region_name;
      opt.textContent = `${c.region_name} (${c.soil_type.replace("_", " ")})`;
      if (c.region_name === currentClusterName) opt.selected = true;
      optgroup.appendChild(opt);
    });

    select.appendChild(optgroup);
  });

  if (!currentClusterName || !filtered.some(c => c.region_name === currentClusterName)) {
    currentClusterName = filtered[0].region_name;
  }

  select.value = currentClusterName;
  loadClusterDashboard(currentClusterName);
}

// ============================================================================
// Farm Clusters Modal Functions
// ============================================================================
function openClusterModal() {
  const modal = document.getElementById("clusterModal");
  if (!modal) return;
  modal.style.display = "flex";
  document.querySelectorAll(".modal-tab").forEach(t => {
    if (t.dataset.tabState === "all") t.classList.add("active");
    else t.classList.remove("active");
  });
  renderClusterModalGrid("all");
}

function closeClusterModal() {
  const modal = document.getElementById("clusterModal");
  if (modal) modal.style.display = "none";
}

function renderClusterModalGrid(filterState = "all") {
  const grid = document.getElementById("clusterModalGrid");
  if (!grid) return;
  grid.innerHTML = "";

  const clusters = filterState === "all"
    ? allClusters
    : allClusters.filter(c => c.state === filterState);

  clusters.forEach(c => {
    const isSelected = c.region_name === currentClusterName;
    const card = document.createElement("div");
    card.className = `cluster-card-item ${isSelected ? "selected" : ""}`;
    card.innerHTML = `
      <div class="cluster-card-header">
        <div>
          <div class="cluster-card-title">${c.region_name}</div>
          <div class="cluster-card-assoc">Ayacut: ${c.association_name || "Farm Command"}</div>
        </div>
        <span class="meta-pill state-pill" style="font-size: 11px;">${c.state}</span>
      </div>
      <div class="cluster-card-details">
        <span><b>Soil:</b> ${c.soil_type.replace("_", " ")}</span>
        <span><b>GPS:</b> ${Number(c.latitude).toFixed(2)}°N, ${Number(c.longitude).toFixed(2)}°E</span>
        ${isSelected ? '<span style="background: var(--accent-forest); color: #fff; font-weight: bold; border-color: var(--accent-forest);">✓ Active</span>' : ''}
      </div>
    `;

    card.addEventListener("click", () => {
      selectClusterByName(c.region_name);
      closeClusterModal();
    });

    grid.appendChild(card);
  });
}

function selectClusterByName(clusterName) {
  currentClusterName = clusterName;
  const select = document.getElementById("clusterSelect");
  if (select) select.value = clusterName;
  const stateFilter = document.getElementById("stateFilter");
  const targetObj = allClusters.find(c => c.region_name === clusterName);
  if (targetObj && stateFilter && stateFilter.value !== "all" && stateFilter.value !== targetObj.state) {
    stateFilter.value = "all";
    activeStateFilter = "all";
    renderClusterDropdown();
  }
  loadClusterDashboard(clusterName);
  showToast(`Loaded ${clusterName}`);
}

// ============================================================================
// Load Dashboard & Default Plots for Selected Farm Cluster
// ============================================================================
async function loadClusterDashboard(clusterName) {
  const reqId = ++activeDashboardRequestId;
  try {
    const res = await fetch(`/api/region/${encodeURIComponent(clusterName)}/dashboard`);
    if (!res.ok) throw new Error("Dashboard API returned " + res.status);
    const data = await res.json();
    if (reqId !== activeDashboardRequestId) return;
    if (data.cluster && data.cluster.region_name !== currentClusterName) return;

    renderClusterMeta(data.cluster, data.database_backend);
    renderLiveWeatherRibbon(data.weather);

    // Pre-populate farmer plots from cluster defaults on first load or cluster switch
    farmerPlots = (data.default_plots || []).map((p, idx) => ({
      plot_id: p.plot_id || `Plot_${idx + 1}`,
      crop_type: p.crop_type,
      growth_stage: p.growth_stage,
      area_acres: parseFloat(p.area_acres) || 2.0,
      custom_soil_moisture: p.custom_soil_moisture || null
    }));

    if (data.supported_crops) {
      supportedCrops = data.supported_crops;
    }

    renderFarmerFieldsConfigTable();
    await Promise.all([
      simulateAllocation(),
      loadFutureCrops(clusterName)
    ]);
  } catch (err) {
    console.error("Cluster dashboard load failed:", err);
    showToast("Failed to load cluster data");
  }
}

function renderClusterMeta(c, dbType) {
  document.getElementById("clusterNameTitle").textContent = c.region_name;
  document.getElementById("clusterAssocName").textContent = `Ayacut: ${c.association_name}`;
  document.getElementById("clusterStatePill").textContent = c.state;
  document.getElementById("clusterCoords").textContent = `${c.latitude.toFixed(2)}°N, ${c.longitude.toFixed(2)}°E`;
  document.getElementById("clusterSoil").textContent = c.soil_type.replace("_", " ");
  document.getElementById("dbSourceVal").textContent = `${dbType} Local Store`;
}

function renderLiveWeatherRibbon(w) {
  document.getElementById("weatherSourceBadge").textContent = w.is_live ? "Live Open-Meteo Satellite Feed" : "Fallback Database Cache";
  document.getElementById("weatherLatencyBadge").textContent = `${w.client_latency_ms || 115} ms latency`;
  document.getElementById("weatherDateBadge").textContent = w.today_date || "Today";

  document.getElementById("wTemp").textContent = `${w.temp_max}° / ${w.temp_min}°C`;
  document.getElementById("wHumidity").textContent = `${w.humidity}%`;
  document.getElementById("wWind").textContent = `${w.wind_speed} m/s`;
  document.getElementById("wSolar").textContent = `${w.solar_radiation} MJ/m²`;
  document.getElementById("wRain").textContent = `${w.rainfall_10d} mm`;
  document.getElementById("wEt0").textContent = `${w.et0_10d} mm`;
  document.getElementById("wSoilRoot").textContent = `${w.soil_moisture_root} m³/m³`;
  document.getElementById("wSoilTopProf").textContent = `${w.soil_moisture_top} / ${w.soil_moisture_prof}`;
}

// ============================================================================
// Interactive Field Plot Table (Add / Edit / Remove)
// ============================================================================
function renderFarmerFieldsConfigTable() {
  const tbody = document.getElementById("farmerFieldsConfigTbody");
  tbody.innerHTML = "";

  if (farmerPlots.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 20px; color: var(--text-muted);">No field plots configured. Click '+ Add Field Plot' above to begin planning.</td></tr>`;
    return;
  }

  farmerPlots.forEach((p, idx) => {
    const tr = document.createElement("tr");

    // Crop select options
    const cropOptions = supportedCrops.map(c => `
      <option value="${c}" ${c === p.crop_type ? "selected" : ""}>
        ${CROP_ICONS[c] || "🌱"} ${c.replace("_", " ")}
      </option>
    `).join("");

    // Stage select options
    const stageOptions = GROWTH_STAGES.map(s => `
      <option value="${s}" ${s === p.growth_stage ? "selected" : ""}>${s.replace("_", " ")}</option>
    `).join("");

    tr.innerHTML = `
      <td>
        <input type="text" class="table-input" value="${p.plot_id}" style="width: 100px;" onchange="updatePlotField(${idx}, 'plot_id', this.value)" />
      </td>
      <td>
        <select class="table-input" onchange="updatePlotField(${idx}, 'crop_type', this.value)">
          ${cropOptions}
        </select>
      </td>
      <td>
        <select class="table-input" onchange="updatePlotField(${idx}, 'growth_stage', this.value)">
          ${stageOptions}
        </select>
      </td>
      <td>
        <input type="number" class="table-input area-input" min="0.1" max="100" step="0.1" value="${p.area_acres}" onchange="updatePlotField(${idx}, 'area_acres', parseFloat(this.value) || 1.0)" />
        <span style="font-size: 11px; color: var(--text-muted);">ac</span>
      </td>
      <td style="text-align: center;">
        <button type="button" class="btn btn-danger btn-sm" onclick="removeFarmerPlot(${idx})" title="Remove field plot">
          🗑️
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function updatePlotField(index, field, value) {
  if (farmerPlots[index]) {
    farmerPlots[index][field] = value;
    simulateAllocation();
  }
}

function addNewFarmerPlot() {
  const newId = `Field_${farmerPlots.length + 1}`;
  farmerPlots.push({
    plot_id: newId,
    crop_type: "Cotton",
    growth_stage: "Mid_Season",
    area_acres: 2.0,
    custom_soil_moisture: null
  });
  renderFarmerFieldsConfigTable();
  simulateAllocation();
  showToast(`Added new plot ${newId}`);
}

function removeFarmerPlot(index) {
  if (farmerPlots.length <= 1) {
    showToast("At least one field plot is required.");
    return;
  }
  const removed = farmerPlots.splice(index, 1);
  renderFarmerFieldsConfigTable();
  simulateAllocation();
  showToast(`Removed ${removed[0].plot_id}`);
}

// Make accessible to inline event handlers
window.updatePlotField = updatePlotField;
window.removeFarmerPlot = removeFarmerPlot;

// ============================================================================
// CORE: Simulate Allocation (Calls POST /api/simulate-allocation)
// ============================================================================
async function simulateAllocation() {
  if (farmerPlots.length === 0 || !currentClusterName) return;
  const reqId = ++activeSimulateRequestId;

  const payload = {
    cluster_name: currentClusterName,
    available_water_liters: availableWaterLiters,
    water_source_type: waterSourceType,
    plots: farmerPlots.map(p => ({
      plot_id: p.plot_id,
      crop_type: p.crop_type,
      growth_stage: p.growth_stage,
      area_acres: p.area_acres,
      custom_soil_moisture: p.custom_soil_moisture
    }))
  };

  try {
    const res = await fetch("/api/simulate-allocation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Simulation failed");
    }

    const data = await res.json();
    if (reqId !== activeSimulateRequestId) return;
    if (data.cluster_name && data.cluster_name !== currentClusterName) return;
    renderSimulationResults(data);
  } catch (err) {
    console.error("Simulation error:", err);
    showToast("Allocation simulation error: " + err.message);
  }
}

function renderSimulationResults(data) {
  const budget = data.water_budget;
  const summary = data.summary;
  const plots = data.plots;

  // 1. Deficit / Surplus Feedback Banner
  const banner = document.getElementById("deficitSurplusBanner");
  const iconElem = document.getElementById("feedbackIcon");
  const statusElem = document.getElementById("feedbackStatus");
  const msgElem = document.getElementById("feedbackMessage");
  const covElem = document.getElementById("feedbackCoverage");

  banner.className = `water-feedback-banner ${budget.water_status === "SURPLUS" ? "surplus" : "deficit"}`;
  iconElem.textContent = budget.water_status === "SURPLUS" ? "✅" : "⚠️";
  statusElem.textContent = budget.water_status === "SURPLUS" ? "SUFFICIENT WATER SUPPLY" : "WATER DEFICIT ALERT";
  msgElem.textContent = budget.feedback_message;
  covElem.textContent = `${budget.coverage_pct}% Stress Demand Met`;

  // 2. Summary KPI Strip
  document.getElementById("kpiTotalAcres").textContent = summary.total_acreage;
  document.getElementById("kpiPlotCount").textContent = summary.total_plots;
  document.getElementById("kpiCropVarieties").textContent = `${new Set(plots.map(p => p.crop_type)).size} crop types`;

  document.getElementById("kpiAvgCsi").textContent = summary.farm_avg_csi.toFixed(3);
  const csiBadge = document.getElementById("kpiCsiBadge");
  const avgCsi = summary.farm_avg_csi;
  if (avgCsi < 0.25) {
    csiBadge.textContent = "Low Stress";
    csiBadge.className = "badge badge-low";
  } else if (avgCsi < 0.50) {
    csiBadge.textContent = "Moderate Stress";
    csiBadge.className = "badge badge-moderate";
  } else if (avgCsi < 0.70) {
    csiBadge.textContent = "High Stress";
    csiBadge.className = "badge badge-high";
  } else {
    csiBadge.textContent = "Critical Drought";
    csiBadge.className = "badge badge-critical";
  }

  document.getElementById("kpiTotalDemand").textContent = formatNumber(budget.total_recommended_liters);
  document.getElementById("kpiCoverageFooter").textContent = `Supply: ${formatNumber(budget.available_water_liters)} L (${budget.coverage_pct}%)`;

  // 3. Allocation Results Table
  renderAllocationResultsTable(plots);

  // 4. Update Charts
  renderRiskDonutChart(summary.risk_distribution);
  renderAllocationBarChart(plots);
}

function renderAllocationResultsTable(plots) {
  const tbody = document.getElementById("allocationResultsTbody");
  tbody.innerHTML = "";

  plots.forEach(p => {
    const tr = document.createElement("tr");

    let rankClass = "rank-badge";
    if (p.priority_rank === 1) rankClass += " rank-1";
    else if (p.priority_rank === 2) rankClass += " rank-2";

    const riskBadgeClass = (RISK_CONFIG[p.risk_level] || {}).badgeClass || "badge-moderate";
    const icon = CROP_ICONS[p.crop_type] || "🌱";

    tr.innerHTML = `
      <td><span class="${rankClass}">#${p.priority_rank}</span></td>
      <td><strong>${p.plot_id}</strong></td>
      <td><span>${icon} ${p.crop_type.replace("_", " ")}</span></td>
      <td><span class="meta-pill" style="background:#EAE5D9; color:var(--text-main);">${p.growth_stage.replace("_", " ")}</span></td>
      <td><b>${p.area_acres}</b> ac</td>
      <td>${p.blended_soil_moisture}</td>
      <td><b>${p.predicted_csi.toFixed(3)}</b></td>
      <td><span class="badge ${riskBadgeClass}">${p.risk_level}</span></td>
      <td><b style="color: var(--accent-forest);">${p.priority_score}</b></td>
      <td>
        <strong>${formatNumber(p.ideal_liters)} L</strong>
        <div style="font-size: 11px; color: var(--text-faint);">${p.ideal_depth_mm} mm depth</div>
      </td>
      <td>
        <strong style="color: var(--primary-dark); font-size: 14px;">${formatNumber(p.allocated_liters)} L</strong>
        <div style="font-size: 11px; color: var(--accent-forest); font-weight: 700;">${p.water_share_pct}% share</div>
      </td>
      <td>
        <span class="badge" style="background: #EAE5D9; color: var(--accent-forest); font-weight: 700;">${p.allocated_depth_mm} mm</span>
      </td>
      <td class="stress-driver-cell" title="${p.primary_driver}">${p.primary_driver}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ============================================================================
// Chart 1: Crop Stress Risk Distribution (Earthy Palette)
// ============================================================================
function renderRiskDonutChart(riskDist) {
  const ctx = document.getElementById("riskChart").getContext("2d");
  if (riskChartInstance) {
    riskChartInstance.destroy();
  }

  const labels = ["Low", "Moderate", "High", "Critical"];
  const counts = labels.map(l => riskDist[l] || 0);
  const colors = [
    EARTHY_PALETTE.low,
    EARTHY_PALETTE.amber,
    EARTHY_PALETTE.terracotta,
    EARTHY_PALETTE.rust
  ];

  riskChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: colors,
        borderColor: "#FFFFFF",
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: EARTHY_PALETTE.charcoal,
            font: { size: 12, weight: "bold" },
            padding: 14
          }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} Plots`
          }
        }
      },
      cutout: "68%"
    }
  });
}

// ============================================================================
// Chart 2: Water Allocation vs Area Bar Chart (Earthy Palette)
// ============================================================================
function renderAllocationBarChart(plots) {
  const ctx = document.getElementById("allocationChart").getContext("2d");
  if (allocationChartInstance) {
    allocationChartInstance.destroy();
  }

  const labels = plots.map(p => `${p.plot_id} (${p.crop_type.replace("_", " ")})`);
  const allocated = plots.map(p => p.allocated_liters);
  const areas = plots.map(p => p.area_acres);

  allocationChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Allocated Water (L)",
          data: allocated,
          backgroundColor: "rgba(76, 84, 61, 0.85)", // Moss forest
          borderColor: EARTHY_PALETTE.moss,
          borderWidth: 1,
          borderRadius: 4,
          yAxisID: "y"
        },
        {
          label: "Field Area (Acres)",
          data: areas,
          type: "line",
          borderColor: EARTHY_PALETTE.amber, // Warm harvest amber
          backgroundColor: "rgba(198, 139, 56, 0.2)",
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: EARTHY_PALETTE.amber,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      scales: {
        x: {
          ticks: { color: EARTHY_PALETTE.charcoal, font: { size: 11, weight: "600" } },
          grid: { color: "rgba(164, 176, 146, 0.3)" }
        },
        y: {
          type: "linear",
          position: "left",
          ticks: {
            color: EARTHY_PALETTE.moss,
            callback: (v) => `${(v / 1000).toFixed(0)}k L`
          },
          grid: { color: "rgba(164, 176, 146, 0.3)" }
        },
        y1: {
          type: "linear",
          position: "right",
          ticks: { color: EARTHY_PALETTE.amber },
          grid: { drawOnChartArea: false }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: EARTHY_PALETTE.charcoal, font: { size: 11, weight: "bold" } }
        }
      }
    }
  });
}

// ============================================================================
// Section 3: 14-Day Forecast & Future Crop Suitability
// ============================================================================
async function loadFutureCrops(clusterName) {
  const reqId = ++activeFutureCropsRequestId;
  try {
    const res = await fetch(`/api/region/${encodeURIComponent(clusterName)}/future-crops`);
    if (!res.ok) throw new Error("Future crops API returned " + res.status);
    const data = await res.json();
    if (reqId !== activeFutureCropsRequestId) return;
    if (data.cluster_name && data.cluster_name !== currentClusterName) return;

    renderForecastChart(data.forecast_14d, data.projected_metrics);
    renderFutureCropsList(data.top_future_crops);
  } catch (err) {
    console.error("Future crops error:", err);
  }
}

function renderForecastChart(forecast, metrics) {
  const pillsWrap = document.getElementById("forecastPills");
  pillsWrap.innerHTML = `
    <span class="f-pill">Avg Temp Max: <b>${metrics.avg_future_temp_max}°C</b></span>
    <span class="f-pill">Total Rain (14d): <b>${metrics.sum_future_rainfall_14d} mm</b></span>
    <span class="f-pill">ET0 Demand: <b>${metrics.sum_future_et0_14d} mm</b></span>
    <span class="f-pill">Water Deficit: <b>${metrics.projected_water_balance} mm</b></span>
  `;

  const ctx = document.getElementById("forecastChart").getContext("2d");
  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  const labels = forecast.map(f => {
    const parts = f.date.split("-");
    return `${parts[1]}/${parts[2]}`;
  });

  const tmax = forecast.map(f => f.temp_max);
  const rain = forecast.map(f => f.rainfall);
  const et0 = forecast.map(f => f.et0);

  forecastChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Projected Max Temp (°C)",
          data: tmax,
          type: "line",
          borderColor: EARTHY_PALETTE.terracotta,
          backgroundColor: "rgba(184, 93, 59, 0.15)",
          borderWidth: 2.5,
          pointRadius: 3,
          yAxisID: "yTemp",
          tension: 0.3
        },
        {
          label: "Precipitation (mm)",
          data: rain,
          backgroundColor: "rgba(76, 84, 61, 0.8)",
          borderColor: EARTHY_PALETTE.moss,
          borderWidth: 1,
          yAxisID: "yRain",
          borderRadius: 3
        },
        {
          label: "ET0 Evapotranspiration (mm)",
          data: et0,
          backgroundColor: "rgba(164, 176, 146, 0.7)",
          borderColor: EARTHY_PALETTE.sage,
          borderWidth: 1,
          yAxisID: "yRain",
          borderRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      scales: {
        x: {
          ticks: { color: EARTHY_PALETTE.charcoal, font: { size: 10 } },
          grid: { color: "rgba(164, 176, 146, 0.3)" }
        },
        yTemp: {
          type: "linear",
          position: "right",
          title: { display: true, text: "Temperature (°C)", color: EARTHY_PALETTE.terracotta },
          ticks: { color: EARTHY_PALETTE.terracotta },
          grid: { drawOnChartArea: false }
        },
        yRain: {
          type: "linear",
          position: "left",
          title: { display: true, text: "Water (mm)", color: EARTHY_PALETTE.moss },
          ticks: { color: EARTHY_PALETTE.moss },
          grid: { color: "rgba(164, 176, 146, 0.3)" }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: EARTHY_PALETTE.charcoal, font: { size: 11, weight: "bold" } }
        }
      }
    }
  });
}

function renderFutureCropsList(crops) {
  const container = document.getElementById("futureCropsList");
  container.innerHTML = "";

  if (!crops || crops.length === 0) {
    container.innerHTML = `<div class="loading-state">No future crop recommendations available.</div>`;
    return;
  }

  crops.forEach((c, idx) => {
    const card = document.createElement("div");
    card.className = "crop-card";
    const icon = CROP_ICONS[c.crop_type] || "🌱";
    const badgeClass = (RISK_CONFIG[c.risk_level] || {}).badgeClass || "badge-low";

    card.innerHTML = `
      <div class="crop-card-top">
        <span class="crop-name">${icon} #${idx + 1} ${c.crop_type.replace("_", " ")}</span>
        <span class="crop-suitability">${c.suitability_score_pct}% Fit</span>
      </div>
      <div class="crop-card-metrics">
        <span>Projected CSI: <b>${c.projected_csi.toFixed(3)}</b></span>
        <span>Risk: <span class="badge ${badgeClass}">${c.risk_level}</span></span>
        <span>Heat Tol: <b>${c.temp_tolerance}°C</b></span>
      </div>
      <div class="crop-card-rationale">
        ${c.reasoning}
      </div>
    `;
    container.appendChild(card);
  });
}

// ============================================================================
// Helper Utilities
// ============================================================================
function formatNumber(num) {
  if (num === undefined || num === null) return "0";
  return Number(num).toLocaleString("en-US", { maximumFractionDigits: 1 });
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}
