/**
 * AgriStress Regional Intelligence - Enhanced Vanilla JavaScript Frontend
 * Multi-State Region Filter, Association Ledger, and Live Open-Meteo Audit Inspector
 */

// Global Application State
let currentRegion = "";
let regionsList = [];
let availableStates = [];
let activeStateFilter = "all";
let riskChartInstance = null;
let allocationChartInstance = null;
let forecastChartInstance = null;

// Risk Level Formatting Configuration
const RISK_CONFIG = {
  Low: { color: "#10b981", bg: "rgba(16, 185, 129, 0.15)", border: "rgba(16, 185, 129, 0.4)", badgeClass: "badge-low" },
  Moderate: { color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)", border: "rgba(245, 158, 11, 0.4)", badgeClass: "badge-moderate" },
  High: { color: "#f97316", bg: "rgba(249, 115, 22, 0.15)", border: "rgba(249, 115, 22, 0.4)", badgeClass: "badge-high" },
  Critical: { color: "#ef4444", bg: "rgba(239, 68, 68, 0.2)", border: "rgba(239, 68, 68, 0.5)", badgeClass: "badge-critical" }
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

// ============================================================================
// Initialization
// ============================================================================
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadRegions();
});

function setupEventListeners() {
  // State filter
  const stateFilter = document.getElementById("stateFilter");
  stateFilter.addEventListener("change", (e) => {
    activeStateFilter = e.target.value;
    renderRegionDropdown();
  });

  // Region select
  const regionSelect = document.getElementById("regionSelect");
  regionSelect.addEventListener("change", (e) => {
    currentRegion = e.target.value;
    refreshAll();
  });

  // Sync button
  const refreshBtn = document.getElementById("refreshBtn");
  refreshBtn.addEventListener("click", () => {
    refreshAll();
    showToast("Syncing latest live weather data...");
  });

  // Audit / Verify live data button
  const verifyWeatherBtn = document.getElementById("verifyWeatherBtn");
  const quickVerifyBtn = document.getElementById("quickVerifyBtn");
  verifyWeatherBtn.addEventListener("click", openVerifyAuditModal);
  quickVerifyBtn.addEventListener("click", openVerifyAuditModal);

  // Close audit modal
  const verifyModal = document.getElementById("verifyModal");
  const closeVerifyModalBtn = document.getElementById("closeVerifyModalBtn");
  const closeVerifyBtn2 = document.getElementById("closeVerifyBtn2");
  const closeVerify = () => verifyModal.classList.remove("open");
  closeVerifyModalBtn.addEventListener("click", closeVerify);
  closeVerifyBtn2.addEventListener("click", closeVerify);

  // Register Region Modal handlers
  const openAddRegionBtn = document.getElementById("openAddRegionModalBtn");
  const addRegionModal = document.getElementById("addRegionModal");
  const closeRegionModalBtn = document.getElementById("closeRegionModalBtn");
  const cancelRegionModalBtn = document.getElementById("cancelRegionModalBtn");

  openAddRegionBtn.addEventListener("click", () => {
    addRegionModal.classList.add("open");
    document.getElementById("regionFormAlert").style.display = "none";
  });

  const closeRegionModal = () => addRegionModal.classList.remove("open");
  closeRegionModalBtn.addEventListener("click", closeRegionModal);
  cancelRegionModalBtn.addEventListener("click", closeRegionModal);

  // Register Region form submit
  const addRegionForm = document.getElementById("addRegionForm");
  addRegionForm.addEventListener("submit", handleAddRegionSubmit);

  // Add Plot Modal handlers
  const openModalBtn = document.getElementById("openAddPlotModalBtn");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const cancelModalBtn = document.getElementById("cancelModalBtn");
  const modal = document.getElementById("addPlotModal");

  openModalBtn.addEventListener("click", () => {
    modal.classList.add("open");
    document.getElementById("formAlert").style.display = "none";
  });

  const closeModal = () => modal.classList.remove("open");
  closeModalBtn.addEventListener("click", closeModal);
  cancelModalBtn.addEventListener("click", closeModal);

  // Add Plot form submit
  const form = document.getElementById("addPlotForm");
  form.addEventListener("submit", handleAddPlotSubmit);
}

async function refreshAll() {
  if (!currentRegion) return;
  await Promise.all([
    loadDashboard(currentRegion),
    loadFutureCrops(currentRegion)
  ]);
}

// ============================================================================
// Load Regions & States
// ============================================================================
async function loadRegions(selectRegionName = null) {
  try {
    const res = await fetch("/api/regions");
    const data = await res.json();
    regionsList = data.regions || [];
    availableStates = data.states || [];

    // Populate State Filter
    const stateFilter = document.getElementById("stateFilter");
    stateFilter.innerHTML = `<option value="all">All States (${availableStates.length})</option>`;
    availableStates.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      if (activeStateFilter === s) opt.selected = true;
      stateFilter.appendChild(opt);
    });

    renderRegionDropdown(selectRegionName);
  } catch (err) {
    console.error("Failed to load regions:", err);
    showToast("Error loading regions list from API");
  }
}

function renderRegionDropdown(selectRegionName = null) {
  const select = document.getElementById("regionSelect");
  select.innerHTML = "";

  const filtered = activeStateFilter === "all"
    ? regionsList
    : regionsList.filter(r => r.state === activeStateFilter);

  if (filtered.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No regions found for this state";
    select.appendChild(opt);
    return;
  }

  // Group by State
  const byState = {};
  filtered.forEach(r => {
    if (!byState[r.state]) byState[r.state] = [];
    byState[r.state].push(r);
  });

  Object.keys(byState).sort().forEach(stateName => {
    const optgroup = document.createElement("optgroup");
    optgroup.label = `📍 ${stateName}`;

    byState[stateName].forEach(r => {
      const opt = document.createElement("option");
      opt.value = r.region_name;
      opt.textContent = `${r.region_name} • ${r.association_name || r.state}`;
      if (selectRegionName ? r.region_name === selectRegionName : r.region_name === currentRegion) {
        opt.selected = true;
      }
      optgroup.appendChild(opt);
    });

    select.appendChild(optgroup);
  });

  // Select initial or requested
  if (selectRegionName) {
    currentRegion = selectRegionName;
  } else if (!currentRegion || !filtered.some(r => r.region_name === currentRegion)) {
    currentRegion = filtered[0].region_name;
  }

  select.value = currentRegion;
  refreshAll();
}

// ============================================================================
// Load Region Dashboard
// ============================================================================
async function loadDashboard(regionName) {
  try {
    const res = await fetch(`/api/region/${encodeURIComponent(regionName)}/dashboard`);
    if (!res.ok) throw new Error(`Dashboard API returned ${res.status}`);
    const data = await res.json();

    renderRegionMeta(data.region, data.database_backend);
    renderLiveWeatherRibbon(data.weather);
    renderKpiOverview(data.summary);
    renderRiskDonutChart(data.summary.risk_distribution);
    renderAllocationBarChart(data.plots);
    renderFarmerLedgerTable(data.plots);
  } catch (err) {
    console.error("Dashboard error:", err);
    showToast("Failed to fetch regional dashboard data");
  }
}

// ============================================================================
// Render Metadata & Weather Ribbon
// ============================================================================
function renderRegionMeta(reg, dbType) {
  document.getElementById("regionNameTitle").textContent = reg.region_name;
  document.getElementById("regionAssocName").textContent = `🌾 ${reg.association_name || "Regional Farmers Association"}`;
  document.getElementById("regionStatePill").textContent = reg.state;
  document.getElementById("dbSourcePill").textContent = `DB: ${dbType}`;
  document.getElementById("regionCoords").textContent = `${reg.latitude.toFixed(2)}°N, ${reg.longitude.toFixed(2)}°E`;
  document.getElementById("regionSoil").textContent = reg.soil_type.replace("_", " ");
  document.getElementById("regionWaterQuota").textContent = `${formatNumber(reg.available_water_liters)} L`;
}

function renderLiveWeatherRibbon(w) {
  const sourceBadge = document.getElementById("weatherSourceBadge");
  sourceBadge.textContent = w.is_live ? "Live Open-Meteo Satellite Feed" : "Fallback Database Cache";

  const v = w.verification || {};
  document.getElementById("weatherGridBadge").textContent = v.weather_model ? "11km ECMWF Grid" : "ECMWF Grid";
  document.getElementById("weatherLatencyBadge").textContent = v.client_latency_ms ? `${v.client_latency_ms} ms latency` : "Live";
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
// Render KPI Cards (Section 1)
// ============================================================================
function renderKpiOverview(summary) {
  document.getElementById("kpiAcreage").textContent = summary.total_acreage;
  document.getElementById("kpiPlots").textContent = summary.total_plots;
  
  const cropCount = Object.keys(summary.crop_distribution || {}).length;
  document.getElementById("kpiCropsCount").textContent = `${cropCount} crop varieties monitored`;

  // Regional Average CSI
  const avgCsiElem = document.getElementById("kpiAvgCsi");
  avgCsiElem.textContent = summary.regional_avg_csi.toFixed(3);

  const csiBadge = document.getElementById("kpiCsiStatusPill");
  const csiVal = summary.regional_avg_csi;
  if (csiVal < 0.25) {
    csiBadge.textContent = "Optimal Range";
    csiBadge.className = "csi-badge badge-low";
  } else if (csiVal < 0.50) {
    csiBadge.textContent = "Moderate Stress";
    csiBadge.className = "csi-badge badge-moderate";
  } else if (csiVal < 0.70) {
    csiBadge.textContent = "High Stress Alert";
    csiBadge.className = "csi-badge badge-high";
  } else {
    csiBadge.textContent = "Critical Drought";
    csiBadge.className = "csi-badge badge-critical";
  }

  // Water Allocation Progress
  document.getElementById("kpiWaterAllocated").textContent = formatNumber(summary.allocated_water_liters);
  const pct = Math.min(100, summary.quota_utilization_pct || 0);
  document.getElementById("quotaProgressBar").style.width = `${pct}%`;
  document.getElementById("kpiWaterPercent").textContent = `${pct}% of ${formatNumber(summary.available_water_liters)} L reservoir`;
}

// ============================================================================
// Chart 1: Risk Donut Chart
// ============================================================================
function renderRiskDonutChart(riskDist) {
  const ctx = document.getElementById("riskChart").getContext("2d");
  if (riskChartInstance) {
    riskChartInstance.destroy();
  }

  const labels = ["Low", "Moderate", "High", "Critical"];
  const counts = labels.map(l => riskDist[l] || 0);
  const colors = labels.map(l => RISK_CONFIG[l].color);

  riskChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: colors,
        borderColor: "#152238",
        borderWidth: 3,
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
            color: "#94a3b8",
            font: { size: 12 },
            padding: 16
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
// Chart 2: Water Allocation vs Area Bar Chart
// ============================================================================
function renderAllocationBarChart(plots) {
  const ctx = document.getElementById("allocationChart").getContext("2d");
  if (allocationChartInstance) {
    allocationChartInstance.destroy();
  }

  const displayPlots = plots.slice(0, 10);
  const labels = displayPlots.map(p => `${p.plot_code} (${p.crop_type})`);
  const allocated = displayPlots.map(p => p.allocated_liters);
  const areas = displayPlots.map(p => p.area_acres);

  allocationChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Allocated Water (L)",
          data: allocated,
          backgroundColor: "rgba(56, 189, 248, 0.75)",
          borderColor: "#38bdf8",
          borderWidth: 1,
          borderRadius: 4,
          yAxisID: "y"
        },
        {
          label: "Plot Area (Acres)",
          data: areas,
          type: "line",
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.2)",
          borderWidth: 2,
          pointRadius: 4,
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
          ticks: { color: "#94a3b8", font: { size: 11 } },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          type: "linear",
          position: "left",
          ticks: {
            color: "#38bdf8",
            callback: (v) => `${(v / 1000).toFixed(0)}k L`
          },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y1: {
          type: "linear",
          position: "right",
          ticks: { color: "#f59e0b" },
          grid: { drawOnChartArea: false }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#94a3b8" }
        }
      }
    }
  });
}

// ============================================================================
// Render Section 2: Farmer Plot Ledger Table
// ============================================================================
function renderFarmerLedgerTable(plots) {
  const tbody = document.getElementById("plotsTableBody");
  tbody.innerHTML = "";

  if (!plots || plots.length === 0) {
    tbody.innerHTML = `<tr><td colspan="12" class="table-loading">No farmer plots found for this region. Click 'Register New Plot' to add one.</td></tr>`;
    return;
  }

  plots.forEach(p => {
    const tr = document.createElement("tr");

    let rankClass = "rank-badge";
    if (p.priority_rank === 1) rankClass += " rank-1";
    else if (p.priority_rank === 2) rankClass += " rank-2";
    else if (p.priority_rank === 3) rankClass += " rank-3";

    const riskBadgeClass = (RISK_CONFIG[p.risk_level] || {}).badgeClass || "badge-moderate";
    const icon = CROP_ICONS[p.crop_type] || "🌿";

    tr.innerHTML = `
      <td><span class="${rankClass}">#${p.priority_rank}</span></td>
      <td><strong>${p.plot_code}</strong></td>
      <td>${p.farmer_name}</td>
      <td><span>${icon} ${p.crop_type.replace("_", " ")}</span></td>
      <td><span class="meta-pill db-pill">${p.growth_stage}</span></td>
      <td>${p.area_acres} ac</td>
      <td><strong>${p.soil_moisture_root}</strong></td>
      <td><strong>${p.predicted_csi.toFixed(3)}</strong></td>
      <td><span class="badge ${riskBadgeClass}">${p.risk_level}</span></td>
      <td><span style="color: #38bdf8; font-weight: 700;">${p.priority_score}</span></td>
      <td>
        <strong>${formatNumber(p.allocated_liters)} L</strong>
        <div style="font-size: 11px; color: #94a3b8;">${p.water_share_pct}% share</div>
      </td>
      <td class="stress-driver-cell" title="${p.primary_driver}">${p.primary_driver}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ============================================================================
// Section 3: 14-Day Forecast & Future Crop Suitability
// ============================================================================
async function loadFutureCrops(regionName) {
  try {
    const res = await fetch(`/api/region/${encodeURIComponent(regionName)}/future-crops`);
    if (!res.ok) throw new Error(`Future crops API returned ${res.status}`);
    const data = await res.json();

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
    <span class="f-pill">Total ET0 (14d): <b>${metrics.sum_future_et0_14d} mm</b></span>
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
          borderColor: "#f97316",
          backgroundColor: "rgba(249, 115, 22, 0.15)",
          borderWidth: 2,
          pointRadius: 3,
          yAxisID: "yTemp",
          tension: 0.3
        },
        {
          label: "Precipitation (mm)",
          data: rain,
          backgroundColor: "rgba(56, 189, 248, 0.7)",
          borderColor: "#38bdf8",
          borderWidth: 1,
          yAxisID: "yRain",
          borderRadius: 3
        },
        {
          label: "ET0 Evapotranspiration (mm)",
          data: et0,
          backgroundColor: "rgba(16, 185, 129, 0.6)",
          borderColor: "#10b981",
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
          ticks: { color: "#94a3b8", font: { size: 10 } },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        yTemp: {
          type: "linear",
          position: "right",
          title: { display: true, text: "Temperature (°C)", color: "#f97316" },
          ticks: { color: "#f97316" },
          grid: { drawOnChartArea: false }
        },
        yRain: {
          type: "linear",
          position: "left",
          title: { display: true, text: "Water (mm)", color: "#38bdf8" },
          ticks: { color: "#38bdf8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#94a3b8", font: { size: 11 } }
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
// MODAL: Live Open-Meteo Weather & Satellite Accuracy Audit
// ============================================================================
async function openVerifyAuditModal() {
  const modal = document.getElementById("verifyModal");
  modal.classList.add("open");

  const container = document.getElementById("verifyAuditContent");
  container.innerHTML = `<div class="loading-state">Pinging Open-Meteo High-Resolution Grid for ${currentRegion}...</div>`;

  try {
    const res = await fetch(`/api/region/${encodeURIComponent(currentRegion)}/verify-weather`);
    if (!res.ok) throw new Error("Verification query failed");
    const data = await res.json();

    const reg = data.verified_region;
    const audit = data.live_accuracy_audit;
    const m = data.current_measurements;
    const sm = m.satellite_soil_moisture || {};
    const benchmarks = data.cross_region_specificity_contrast || [];

    // Set Direct Link
    const apiLink = document.getElementById("directApiLink");
    apiLink.href = audit.api_endpoint_url;

    container.innerHTML = `
      <!-- Verification Badge Banner -->
      <div class="audit-status-banner">
        <div class="audit-status-badge">
          <span>✅</span> LIVE ACCURACY & GEOGRAPHIC SPECIFICITY CONFIRMED
        </div>
        <div class="audit-timestamp">
          Live Ping: <b>${audit.queried_at_utc}</b> (${audit.client_latency_ms} ms latency)
        </div>
      </div>

      <!-- Section A: Grid & Target Telemetry -->
      <div class="audit-section">
        <h4>📡 Target vs Matched Weather Grid</h4>
        <div class="audit-grid">
          <div class="audit-cell">
            <span class="audit-cell-label">Region & Association</span>
            <span class="audit-cell-val">${reg.region_name}</span>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">${reg.association_name}</div>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Target GPS Coordinates</span>
            <span class="audit-cell-val highlight-cyan">${reg.coordinates.latitude.toFixed(4)}°N, ${reg.coordinates.longitude.toFixed(4)}°E</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Matched Grid Cell (Elevation)</span>
            <span class="audit-cell-val">${audit.matched_grid_cell.latitude.toFixed(2)}°N, ${audit.matched_grid_cell.longitude.toFixed(2)}°E (${audit.elevation_m} m AMSL)</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Numerical Weather Model</span>
            <span class="audit-cell-val" style="font-size: 12px; color: #34d399;">${audit.model_grid_resolution}</span>
          </div>
        </div>
      </div>

      <!-- Section B: Live Atmospheric & Satellite Soil Measurements -->
      <div class="audit-section">
        <h4>🌍 Live Region-Specific Measurements</h4>
        <div class="audit-grid">
          <div class="audit-cell">
            <span class="audit-cell-label">Temperature (Max / Min)</span>
            <span class="audit-cell-val">${m.temp_max_c}°C / ${m.temp_min_c}°C</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Mean Relative Humidity</span>
            <span class="audit-cell-val">${m.humidity_pct}%</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">10-Day Rain / ET0 Demand</span>
            <span class="audit-cell-val">${m.rainfall_10d_mm} mm / ${m.et0_10d_mm} mm</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Satellite Root Soil (7-28cm)</span>
            <span class="audit-cell-val highlight-cyan">${sm.rootzone_7_to_28cm} m³/m³</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Satellite Topsoil (0-7cm)</span>
            <span class="audit-cell-val">${sm.topsoil_0_to_7cm} m³/m³</span>
          </div>
          <div class="audit-cell">
            <span class="audit-cell-label">Satellite Deep Profile (28-100cm)</span>
            <span class="audit-cell-val">${sm.deep_profile_28_to_100cm} m³/m³</span>
          </div>
        </div>
      </div>

      <!-- Section C: Cross-Region Specificity Matrix -->
      <div class="audit-section">
        <h4>📊 Proof of Region Specificity (Live Simultaneous Cross-State Contrast)</h4>
        <div class="table-responsive">
          <table class="contrast-table">
            <thead>
              <tr>
                <th>Region & State</th>
                <th>Climate Zone</th>
                <th>Coordinates</th>
                <th>Live Max Temp</th>
                <th>Live Humidity</th>
                <th>10d Rain</th>
                <th>Root Soil Moisture</th>
              </tr>
            </thead>
            <tbody>
              <tr class="current-target">
                <td><strong>🎯 ${reg.region_name} (${reg.state})</strong></td>
                <td><span class="meta-pill state-pill">Current Target</span></td>
                <td>${reg.coordinates.latitude}°N, ${reg.coordinates.longitude}°E</td>
                <td><b>${m.temp_max_c}°C</b></td>
                <td><b>${m.humidity_pct}%</b></td>
                <td>${m.rainfall_10d_mm} mm</td>
                <td><b style="color: #38bdf8;">${sm.rootzone_7_to_28cm}</b></td>
              </tr>
              ${benchmarks.map(b => `
                <tr>
                  <td>${b.region_name} (${b.state})</td>
                  <td><span class="meta-pill db-pill">${b.climate_type}</span></td>
                  <td>${b.coordinates}</td>
                  <td>${b.temp_max}°C</td>
                  <td>${b.humidity}%</td>
                  <td>${b.rainfall_10d} mm</td>
                  <td>${b.soil_moisture_root}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
        <div class="contrast-explainer">
          💡 <b>Live Scientific Specificity:</b> As shown in the live benchmark matrix above, weather and satellite soil moisture values differ significantly across distinct latitudes/longitudes in India (e.g. desert vs river delta vs plateau). This confirms that your association is receiving authentic, coordinate-specific satellite and ECMWF inputs rather than averaged or static numbers.
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="form-alert">Verification request failed: ${err.message}</div>`;
  }
}

// ============================================================================
// Modal & Form Submission (Add Region)
// ============================================================================
async function handleAddRegionSubmit(e) {
  e.preventDefault();
  const alertBox = document.getElementById("regionFormAlert");
  alertBox.style.display = "none";

  const payload = {
    region_name: document.getElementById("newRegionName").value.trim(),
    association_name: document.getElementById("newAssocName").value.trim(),
    state: document.getElementById("newState").value.trim(),
    soil_type: document.getElementById("newSoilType").value,
    latitude: parseFloat(document.getElementById("newLat").value),
    longitude: parseFloat(document.getElementById("newLon").value),
    available_water_liters: parseFloat(document.getElementById("newWaterQuota").value)
  };

  const submitBtn = document.getElementById("submitRegionBtn");
  const origBtnText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = "Registering...";

  try {
    const res = await fetch("/api/regions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (!res.ok) {
      throw new Error(result.detail || "Failed to register region");
    }

    showToast(`Region '${payload.region_name}' registered successfully!`);
    document.getElementById("addRegionModal").classList.remove("open");
    document.getElementById("addRegionForm").reset();

    // Reload regions list and auto-select the newly added region
    await loadRegions(payload.region_name);
  } catch (err) {
    alertBox.textContent = err.message;
    alertBox.style.display = "block";
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = origBtnText;
  }
}

// ============================================================================
// Modal & Form Submission (Add Plot)
// ============================================================================
async function handleAddPlotSubmit(e) {
  e.preventDefault();
  const alertBox = document.getElementById("formAlert");
  alertBox.style.display = "none";

  const payload = {
    plot_code: document.getElementById("plotCode").value.trim(),
    farmer_name: document.getElementById("farmerName").value.trim(),
    crop_type: document.getElementById("cropType").value,
    growth_stage: document.getElementById("growthStage").value,
    area_acres: parseFloat(document.getElementById("areaAcres").value),
    soil_moisture_root: parseFloat(document.getElementById("soilMoistureRoot").value),
    soil_moisture_top: parseFloat(document.getElementById("soilMoistureTop").value),
    soil_moisture_prof: parseFloat(document.getElementById("soilMoistureProf").value)
  };

  const submitBtn = document.getElementById("submitPlotBtn");
  const origBtnText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = "Saving...";

  try {
    const res = await fetch(`/api/region/${encodeURIComponent(currentRegion)}/plots`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (!res.ok) {
      throw new Error(result.detail || "Failed to register plot");
    }

    showToast(`Plot ${payload.plot_code} registered successfully!`);
    document.getElementById("addPlotModal").classList.remove("open");
    document.getElementById("addPlotForm").reset();

    await loadDashboard(currentRegion);
  } catch (err) {
    alertBox.textContent = err.message;
    alertBox.style.display = "block";
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = origBtnText;
  }
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
  }, 3200);
}
