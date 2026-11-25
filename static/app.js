/**
 * AgriStress — Farmer Water & Crop Allocator
 * Clean Vanilla JavaScript Frontend (No Build Tools)
 * Interactive Field Planning, Open-Meteo Integration, Multi-Language i18n (English, Telugu, Hindi)
 */

// Global Translation Dictionary Reference
const TRANSLATIONS = window.TRANSLATIONS || {};

// Built-in Farm Clusters Fallback (AP & Telangana)
const FALLBACK_CLUSTERS = [
  { region_name: "Shadnagar Ayacut Cluster", state: "Telangana", soil_type: "Red_Sandy", latitude: 17.07, longitude: 78.21, association_name: "Shadnagar Red Soil Farmers Ayacut Union" },
  { region_name: "Miryalaguda Canal Command", state: "Telangana", soil_type: "Black_Clay", latitude: 16.87, longitude: 79.56, association_name: "Nagarjuna Sagar Left Canal Farmers Society" },
  { region_name: "Bodhan Nizamsagar Block", state: "Telangana", soil_type: "Black_Clay", latitude: 18.66, longitude: 77.88, association_name: "Nizamsagar Distributary Ayacut Committee" },
  { region_name: "Siddipet Komaticheruvu Farms", state: "Telangana", soil_type: "Red_Sandy", latitude: 18.10, longitude: 78.85, association_name: "Komaticheruvu Tank Irrigation Collective" },
  { region_name: "Tenali Western Canal Block", state: "Andhra Pradesh", soil_type: "Alluvial_Loam", latitude: 16.24, longitude: 80.64, association_name: "Krishna Western Delta Water Users Association" },
  { region_name: "Anantapur Tadipatri Drip Zone", state: "Andhra Pradesh", soil_type: "Red_Sandy", latitude: 14.91, longitude: 78.01, association_name: "Tadipatri Micro-Irrigation Growers Federation" },
  { region_name: "Bhimavaram Godavari Delta Block", state: "Andhra Pradesh", soil_type: "Alluvial_Loam", latitude: 16.54, longitude: 81.52, association_name: "Godavari Western Canal Ayacut Council" },
  { region_name: "Nandyal KC Canal Ayacut", state: "Andhra Pradesh", soil_type: "Black_Clay", latitude: 15.48, longitude: 78.48, association_name: "Kurnool-Cuddapah Canal Farmers Union" }
];

// Application State
let allClusters = [...FALLBACK_CLUSTERS];
let currentClusterName = "Shadnagar Ayacut Cluster";
let activeStateFilter = "all";
let availableWaterLiters = 50000;
let waterSourceType = "Borewell";
let farmerPlots = [];
let supportedCrops = [];

// Active Language State (en, te, hi)
let currentLang = "en";

// Cached Data for Dynamic Re-translation
let lastClusterMeta = null;
let lastWeatherData = null;
let lastSimulationData = null;
let lastForecastData = null;
let lastProjectedMetrics = null;
let lastFutureCropsData = null;

// Request Concurrency Guards (avoids race condition on rapid switching)
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
  Okra_Export: "🥬",
  Wheat: "🌾",
  Sugarcane: "🎋",
  Chilli: "🌶️",
  Sorghum: "🌾",
  Pearl_Millet: "🌾",
  Pigeon_Pea: "🌱",
  Chickpea: "🌱",
  Sunflower: "🌻",
  Tomato: "🍅"
};

// Growth Stage Options (English backend keys)
const GROWTH_STAGES = ["Initial", "Development", "Mid_Season", "Late_Season"];

// ============================================================================
// Initialization & Event Binding (Safe from DOM Ready / Caching States)
// ============================================================================
function initApp() {
  if (window.location.protocol === "file:") {
    const banner = document.createElement("div");
    banner.style.cssText = "background: #9E2A2B; color: #FFFFFF; padding: 12px 20px; font-weight: bold; text-align: center; font-size: 13px; position: sticky; top: 0; z-index: 9999; box-shadow: 0 4px 10px rgba(0,0,0,0.3);";
    banner.innerHTML = "⚠️ You opened index.html directly from disk (file://). Please navigate to <a href='http://localhost:8000' style='color: #F4F1E8; text-decoration: underline; margin-left: 6px;'>http://localhost:8000</a> in your browser to access the backend API and live Open-Meteo satellite feed.";
    document.body.prepend(banner);
  }

  try {
    setupEventListeners();
  } catch (err) {
    console.warn("Event listeners setup warning:", err);
  }

  // Pre-Dashboard Language Check
  const savedLang = localStorage.getItem("app_lang");
  const welcomeModal = document.getElementById("welcomeLangModal");

  if (!savedLang) {
    // First visit: show Pre-Dashboard Language Selection Welcome Screen
    currentLang = "en";
    if (welcomeModal) welcomeModal.style.display = "flex";
  } else {
    currentLang = ["en", "te", "hi"].includes(savedLang) ? savedLang : "en";
    if (welcomeModal) welcomeModal.style.display = "none";
  }

  applyLanguage(currentLang);
  renderClusterDropdown();
  loadClusters();
  loadClusterDashboard(currentClusterName);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}

function setupEventListeners() {
  // Pre-Dashboard Language Selection Modal Handlers
  document.querySelectorAll(".lang-option-card").forEach(card => {
    card.addEventListener("click", (e) => {
      const chosenLang = card.dataset.lang;
      if (chosenLang && ["en", "te", "hi"].includes(chosenLang)) {
        setLanguage(chosenLang);
        const welcomeModal = document.getElementById("welcomeLangModal");
        if (welcomeModal) welcomeModal.style.display = "none";
        loadClusterDashboard(currentClusterName);
      }
    });
  });

  // Top Navbar Compact Language Switcher Pill
  document.querySelectorAll(".lang-pill-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const chosenLang = btn.dataset.lang;
      if (chosenLang && ["en", "te", "hi"].includes(chosenLang)) {
        setLanguage(chosenLang);
      }
    });
  });

  // State filter
  const stateFilter = document.getElementById("stateFilter");
  if (stateFilter) {
    stateFilter.addEventListener("change", (e) => {
      activeStateFilter = e.target.value;
      renderClusterDropdown();
    });
  }

  // Cluster selector
  const clusterSelect = document.getElementById("clusterSelect");
  if (clusterSelect) {
    clusterSelect.addEventListener("change", (e) => {
      currentClusterName = e.target.value;
      loadClusterDashboard(currentClusterName);
    });
  }

  // Cluster control box click opens select
  const clusterBox = document.getElementById("clusterControlBox");
  if (clusterBox && clusterSelect) {
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
    if (e.key === "Escape") {
      closeClusterModal();
      const welcomeModal = document.getElementById("welcomeLangModal");
      if (welcomeModal && localStorage.getItem("app_lang")) {
        welcomeModal.style.display = "none";
      }
    }
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
  if (syncBtn) {
    syncBtn.addEventListener("click", () => {
      const msg = currentLang === "te" 
        ? "ఉపగ్రహ సమాచారాన్ని రీఫ్రెష్ చేస్తోంది..."
        : (currentLang === "hi" ? "लाइव उपग्रह मौसम डेटा रीफ़्रेश किया जा रहा है..." : "Re-fetching live Open-Meteo satellite feed...");
      showToast(msg);
      loadClusterDashboard(currentClusterName);
    });
  }

  // Water supply numeric input
  const waterInput = document.getElementById("waterSupplyInput");
  const waterSlider = document.getElementById("waterSupplySlider");

  if (waterInput && waterSlider) {
    waterInput.addEventListener("change", (e) => {
      const val = Math.max(1000, parseFloat(e.target.value) || 10000);
      availableWaterLiters = val;
      waterSlider.value = Math.min(val, parseFloat(waterSlider.max));
      simulateAllocation();
    });

    waterSlider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      availableWaterLiters = val;
      waterInput.value = val;
      simulateAllocation();
    });
  }

  // Quick preset buttons
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const val = parseFloat(btn.dataset.liters);
      availableWaterLiters = val;
      if (waterInput) waterInput.value = val;
      if (waterSlider) waterSlider.value = Math.min(val, parseFloat(waterSlider.max));
      simulateAllocation();
    });
  });

  // Water source selector
  const waterSourceSelect = document.getElementById("waterSourceSelect");
  if (waterSourceSelect) {
    waterSourceSelect.addEventListener("change", (e) => {
      waterSourceType = e.target.value;
      simulateAllocation();
    });
  }

  // Add Plot Button
  const addPlotBtn = document.getElementById("addPlotBtn");
  if (addPlotBtn) addPlotBtn.addEventListener("click", addNewFarmerPlot);

  // Recalculate Button
  const recalcBtn = document.getElementById("recalculateBtn");
  if (recalcBtn) {
    recalcBtn.addEventListener("click", () => {
      simulateAllocation();
      const msg = currentLang === "te"
        ? "ఉపగ్రహ సమాచారంతో నీటి కేటాయింపులు లెక్కించబడ్డాయి."
        : (currentLang === "hi" ? "लाइव उपग्रह डेटा के साथ सिंचाई आवंटन की गणना की गई।" : "Allocation recalculated with live ECMWF satellite feed.");
      showToast(msg);
    });
  }
}

// ============================================================================
// Multi-Language Management & Dynamic DOM Translation
// ============================================================================
function setLanguage(lang) {
  if (!["en", "te", "hi"].includes(lang)) lang = "en";
  currentLang = lang;
  localStorage.setItem("app_lang", lang);
  applyLanguage(lang);

  const toastMsg = lang === "te"
    ? "భాషను తెలుగులోకి మార్చడం జరిగింది"
    : (lang === "hi" ? "भाषा को हिन्दी में बदल दिया गया है" : "Language switched to English");
  showToast(toastMsg);
}

function applyLanguage(lang) {
  const dicts = window.TRANSLATIONS || TRANSLATIONS || {};
  if (!dicts[lang]) lang = "en";
  currentLang = lang;

  // 1. Update Document Title
  const metaTitle = TRANSLATIONS[lang]?.meta?.title;
  if (metaTitle) document.title = metaTitle;

  // 2. Update all static [data-i18n] text nodes
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const keyPath = el.getAttribute("data-i18n");
    const val = getNestedTranslation(TRANSLATIONS[lang], keyPath);
    if (val !== undefined) {
      el.textContent = val;
    }
  });

  // 3. Update optgroups in clusterSelect
  document.querySelectorAll("[data-i18n-optgroup]").forEach(el => {
    const stateKey = el.getAttribute("data-i18n-optgroup");
    const translatedState = TRANSLATIONS[lang]?.states?.[stateKey] || stateKey;
    el.label = `📍 ${translatedState}`;
  });

  // 4. Update Header Language Switcher Pill Active Classes
  document.querySelectorAll(".lang-pill-btn").forEach(btn => {
    if (btn.dataset.lang === lang) btn.classList.add("active");
    else btn.classList.remove("active");
  });

  // 5. Update State Filter options
  const stateFilter = document.getElementById("stateFilter");
  if (stateFilter) {
    Array.from(stateFilter.options).forEach(opt => {
      if (opt.value === "all") opt.textContent = TRANSLATIONS[lang]?.states?.all || "All States";
      else if (opt.value === "Telangana") opt.textContent = TRANSLATIONS[lang]?.states?.Telangana || "Telangana";
      else if (opt.value === "Andhra Pradesh") opt.textContent = TRANSLATIONS[lang]?.states?.["Andhra Pradesh"] || "Andhra Pradesh";
    });
  }

  // 6. Update Water Source selector options
  const waterSourceSelect = document.getElementById("waterSourceSelect");
  if (waterSourceSelect) {
    Array.from(waterSourceSelect.options).forEach(opt => {
      const trans = TRANSLATIONS[lang]?.sources?.[opt.value];
      if (trans) opt.textContent = trans;
    });
  }

  // 7. Update Cluster metadata display
  if (lastClusterMeta) {
    renderClusterMeta(lastClusterMeta.cluster, lastClusterMeta.dbType);
  }

  // 8. Update Weather Ribbon display
  if (lastWeatherData) {
    renderLiveWeatherRibbon(lastWeatherData);
  }

  // 9. Re-render cluster dropdown with localized soil labels
  renderClusterDropdown();

  // 10. Re-render farmer fields config table with translated crop/stage labels
  renderFarmerFieldsConfigTable();

  // 11. Re-render simulation results table and charts
  if (lastSimulationData) {
    renderSimulationResults(lastSimulationData);
  }

  // 12. Re-render future crops list and forecast chart
  if (lastForecastData && lastProjectedMetrics) {
    renderForecastChart(lastForecastData, lastProjectedMetrics);
  }
  if (lastFutureCropsData) {
    renderFutureCropsList(lastFutureCropsData);
  }

  // 13. If cluster modal is open, re-render its grid
  const modal = document.getElementById("clusterModal");
  if (modal && modal.style.display !== "none") {
    const activeTab = document.querySelector(".modal-tab.active");
    const tabState = activeTab ? activeTab.dataset.tabState : "all";
    renderClusterModalGrid(tabState);
  }
}

function getNestedTranslation(obj, path) {
  if (!obj || !path) return undefined;
  const parts = path.split(".");
  let cur = obj;
  for (const p of parts) {
    if (cur[p] === undefined) return undefined;
    cur = cur[p];
  }
  return cur;
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

  const soilWord = TRANSLATIONS[currentLang]?.modal?.soil_label || "Soil:";
  const gpsWord = TRANSLATIONS[currentLang]?.modal?.gps_label || "GPS:";
  const activeWord = TRANSLATIONS[currentLang]?.modal?.active_badge || "✓ Active";
  const ayacutWord = TRANSLATIONS[currentLang]?.weather?.ayacut_prefix || "Ayacut: ";

  clusters.forEach(c => {
    const isSelected = c.region_name === currentClusterName;
    const soilLabel = TRANSLATIONS[currentLang]?.soils[c.soil_type] || c.soil_type.replace("_", " ");
    const stateLabel = TRANSLATIONS[currentLang]?.states[c.state] || c.state;

    const card = document.createElement("div");
    card.className = `cluster-card-item ${isSelected ? "selected" : ""}`;
    card.innerHTML = `
      <div class="cluster-card-header">
        <div>
          <div class="cluster-card-title">${c.region_name}</div>
          <div class="cluster-card-assoc">${ayacutWord}${c.association_name || "Farm Command"}</div>
        </div>
        <span class="meta-pill state-pill" style="font-size: 11px;">${stateLabel}</span>
      </div>
      <div class="cluster-card-details">
        <span><b>${soilWord}</b> ${soilLabel}</span>
        <span><b>${gpsWord}</b> ${Number(c.latitude).toFixed(2)}°N, ${Number(c.longitude).toFixed(2)}°E</span>
        ${isSelected ? `<span style="background: var(--accent-forest); color: #fff; font-weight: bold; border-color: var(--accent-forest);">${activeWord}</span>` : ''}
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
// Load Farm Clusters & Populate Dropdowns
// ============================================================================
async function loadClusters() {
  try {
    const res = await fetch("/api/regions");
    if (!res.ok) throw new Error("API status " + res.status);
    const data = await res.json();
    if (data.regions && data.regions.length > 0) {
      allClusters = data.regions;
    }
    supportedCrops = data.supported_crops || Object.keys(CROP_ICONS);
  } catch (err) {
    console.warn("Using built-in clusters:", err);
  } finally {
    renderClusterDropdown();
    if (!lastSimulationData) {
      loadClusterDashboard(currentClusterName);
    }
  }
}

function renderClusterDropdown() {
  const select = document.getElementById("clusterSelect");
  if (!select) return;
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
    const translatedState = TRANSLATIONS[currentLang]?.states?.[stateName] || stateName;
    optgroup.label = `📍 ${translatedState}`;

    byState[stateName].forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.region_name;
      const soilLabel = TRANSLATIONS[currentLang]?.soils[c.soil_type] || c.soil_type.replace("_", " ");
      opt.textContent = `${c.region_name} (${soilLabel})`;
      if (c.region_name === currentClusterName) opt.selected = true;
      optgroup.appendChild(opt);
    });

    select.appendChild(optgroup);
  });

  if (!currentClusterName || !filtered.some(c => c.region_name === currentClusterName)) {
    currentClusterName = filtered[0].region_name;
  }

  select.value = currentClusterName;
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
  lastClusterMeta = { cluster: c, dbType };
  document.getElementById("clusterNameTitle").textContent = c.region_name;

  const ayacutLabel = TRANSLATIONS[currentLang]?.weather?.ayacut_prefix || "Ayacut: ";
  document.getElementById("clusterAssocName").textContent = `${ayacutLabel}${c.association_name}`;

  const stateLabel = TRANSLATIONS[currentLang]?.states[c.state] || c.state;
  document.getElementById("clusterStatePill").textContent = stateLabel;

  document.getElementById("clusterCoords").textContent = `${c.latitude.toFixed(2)}°N, ${c.longitude.toFixed(2)}°E`;

  const soilLabel = TRANSLATIONS[currentLang]?.soils[c.soil_type] || c.soil_type.replace("_", " ");
  document.getElementById("clusterSoil").textContent = soilLabel;

  const storeLabel = TRANSLATIONS[currentLang]?.weather?.db_store || "Database Store";
  document.getElementById("dbSourceVal").textContent = `${dbType} Local Store`;
}

function renderLiveWeatherRibbon(w) {
  lastWeatherData = w;
  const sourceLabel = w.is_live 
    ? (TRANSLATIONS[currentLang]?.weather?.source_live || "Live Open-Meteo Satellite Feed")
    : (TRANSLATIONS[currentLang]?.weather?.source_cache || "Fallback Database Cache");
  document.getElementById("weatherSourceBadge").textContent = sourceLabel;

  const latSuffix = TRANSLATIONS[currentLang]?.weather?.latency_suffix || "ms latency";
  document.getElementById("weatherLatencyBadge").textContent = `${w.client_latency_ms || 115} ${latSuffix}`;

  document.getElementById("weatherDateBadge").textContent = w.today_date || (TRANSLATIONS[currentLang]?.weather?.today || "Today");

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
  if (!tbody) return;
  tbody.innerHTML = "";

  if (farmerPlots.length === 0) {
    const emptyMsg = currentLang === "te"
      ? "పొలాల వివరాలు నమోదు కాలేదు. ప్రణాళిక ప్రారంభించడానికి పైన '+ పొలాన్ని చేర్చండి' క్లిక్ చేయండి."
      : (currentLang === "hi"
          ? "कोई खेत कॉन्फ़िगर नहीं किया गया। योजना शुरू करने के लिए ऊपर '+ खेत जोड़ें' पर क्लिक करें।"
          : "No field plots configured. Click '+ Add Field Plot' above to begin planning.");
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 20px; color: var(--text-muted);">${emptyMsg}</td></tr>`;
    return;
  }

  farmerPlots.forEach((p, idx) => {
    const tr = document.createElement("tr");

    // Crop select options - localized display, original English value
    const cropOptions = supportedCrops.map(c => {
      const translatedCrop = TRANSLATIONS[currentLang]?.crops[c] || c.replace("_", " ");
      return `<option value="${c}" ${c === p.crop_type ? "selected" : ""}>
        ${CROP_ICONS[c] || "🌱"} ${translatedCrop}
      </option>`;
    }).join("");

    // Stage select options - localized display, original English value
    const stageOptions = GROWTH_STAGES.map(s => {
      const translatedStage = TRANSLATIONS[currentLang]?.stages[s] || s.replace("_", " ");
      return `<option value="${s}" ${s === p.growth_stage ? "selected" : ""}>${translatedStage}</option>`;
    }).join("");

    const acLabel = currentLang === "te" ? "ఎక." : (currentLang === "hi" ? "एकड़" : "ac");
    const removeBtnTitle = TRANSLATIONS[currentLang]?.planner?.btn_remove || "Remove";

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
        <span style="font-size: 11px; color: var(--text-muted);">${acLabel}</span>
      </td>
      <td style="text-align: center;">
        <button type="button" class="btn btn-danger btn-sm" onclick="removeFarmerPlot(${idx})" title="${removeBtnTitle}">
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
  const msg = currentLang === "te" ? `కొత్త పొలం ${newId} చేర్చబడింది` : (currentLang === "hi" ? `नया खेत ${newId} जोड़ा गया` : `Added new plot ${newId}`);
  showToast(msg);
}

function removeFarmerPlot(index) {
  if (farmerPlots.length <= 1) {
    const warning = currentLang === "te" ? "కనీసం ఒక పొలం నమోదు తప్పనిసరి." : (currentLang === "hi" ? "कम से कम एक खेत का होना अनिवार्य है।" : "At least one field plot is required.");
    showToast(warning);
    return;
  }
  const removed = farmerPlots.splice(index, 1);
  renderFarmerFieldsConfigTable();
  simulateAllocation();
  const msg = currentLang === "te" ? `${removed[0].plot_id} తొలగించబడింది` : (currentLang === "hi" ? `${removed[0].plot_id} हटाया गया` : `Removed ${removed[0].plot_id}`);
  showToast(msg);
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
  lastSimulationData = data;
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

  const statusText = budget.water_status === "SURPLUS"
    ? (TRANSLATIONS[currentLang]?.planner?.status_surplus || "SUFFICIENT WATER SUPPLY")
    : (TRANSLATIONS[currentLang]?.planner?.status_deficit || "WATER DEFICIT ALERT");
  statusElem.textContent = statusText;

  msgElem.textContent = generateFeedbackMessage(
    budget.water_status,
    budget.available_water_liters,
    budget.water_balance_liters,
    budget.coverage_pct,
    currentLang
  );

  const demandMetText = TRANSLATIONS[currentLang]?.planner?.stress_met_suffix || "Stress Demand Met";
  covElem.textContent = `${budget.coverage_pct}% ${demandMetText}`;

  // 2. Summary KPI Strip
  document.getElementById("kpiTotalAcres").textContent = summary.total_acreage;
  document.getElementById("kpiPlotCount").textContent = summary.total_plots;

  const varietiesWord = TRANSLATIONS[currentLang]?.kpi?.varieties_unit || "crop types";
  document.getElementById("kpiCropVarieties").textContent = `${new Set(plots.map(p => p.crop_type)).size} ${varietiesWord}`;

  document.getElementById("kpiAvgCsi").textContent = summary.farm_avg_csi.toFixed(3);
  const csiBadge = document.getElementById("kpiCsiBadge");
  const avgCsi = summary.farm_avg_csi;

  const riskLabels = TRANSLATIONS[currentLang]?.risks || {};
  if (avgCsi < 0.25) {
    csiBadge.textContent = riskLabels.Low || "Low Stress";
    csiBadge.className = "badge badge-low";
  } else if (avgCsi < 0.50) {
    csiBadge.textContent = riskLabels.Moderate || "Moderate Stress";
    csiBadge.className = "badge badge-moderate";
  } else if (avgCsi < 0.70) {
    csiBadge.textContent = riskLabels.High || "High Stress";
    csiBadge.className = "badge badge-high";
  } else {
    csiBadge.textContent = riskLabels.Critical || "Critical Drought";
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
  if (!tbody) return;
  tbody.innerHTML = "";

  plots.forEach(p => {
    const tr = document.createElement("tr");

    let rankClass = "rank-badge";
    if (p.priority_rank === 1) rankClass += " rank-1";
    else if (p.priority_rank === 2) rankClass += " rank-2";

    const riskBadgeClass = (RISK_CONFIG[p.risk_level] || {}).badgeClass || "badge-moderate";
    const icon = CROP_ICONS[p.crop_type] || "🌱";
    const cropLabel = TRANSLATIONS[currentLang]?.crops[p.crop_type] || p.crop_type.replace("_", " ");
    const stageLabel = TRANSLATIONS[currentLang]?.stages[p.growth_stage] || p.growth_stage.replace("_", " ");
    const riskLabel = TRANSLATIONS[currentLang]?.risks[p.risk_level] || p.risk_level;
    const translatedDriver = translateStressDriver(p.primary_driver, currentLang);
    const depthWord = currentLang === "te" ? "లోతు" : (currentLang === "hi" ? "गहराई" : "depth");
    const shareWord = currentLang === "te" ? "వాటా" : (currentLang === "hi" ? "हिस्सा" : "share");
    const acWord = currentLang === "te" ? "ఎక." : (currentLang === "hi" ? "एकड़" : "ac");

    tr.innerHTML = `
      <td><span class="${rankClass}">#${p.priority_rank}</span></td>
      <td><strong>${p.plot_id}</strong></td>
      <td><span>${icon} ${cropLabel}</span></td>
      <td><span class="meta-pill" style="background:#EAE5D9; color:var(--text-main); font-size:11px;">${stageLabel}</span></td>
      <td><b>${p.area_acres}</b> ${acWord}</td>
      <td>${p.blended_soil_moisture}</td>
      <td><b>${p.predicted_csi.toFixed(3)}</b></td>
      <td><span class="badge ${riskBadgeClass}">${riskLabel}</span></td>
      <td><b style="color: var(--accent-forest);">${p.priority_score}</b></td>
      <td>
        <strong>${formatNumber(p.ideal_liters)} L</strong>
        <div style="font-size: 11px; color: var(--text-faint);">${p.ideal_depth_mm} mm ${depthWord}</div>
      </td>
      <td>
        <strong style="color: var(--primary-dark); font-size: 14px;">${formatNumber(p.allocated_liters)} L</strong>
        <div style="font-size: 11px; color: var(--accent-forest); font-weight: 700;">${p.water_share_pct}% ${shareWord}</div>
      </td>
      <td>
        <span class="badge" style="background: #EAE5D9; color: var(--accent-forest); font-weight: 700;">${p.allocated_depth_mm} mm</span>
      </td>
      <td class="stress-driver-cell" title="${translatedDriver}">${translatedDriver}</td>
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

  const rawLabels = ["Low", "Moderate", "High", "Critical"];
  const displayLabels = rawLabels.map(l => TRANSLATIONS[currentLang]?.risks[l] || l);
  const counts = rawLabels.map(l => riskDist[l] || 0);
  const colors = [
    EARTHY_PALETTE.low,
    EARTHY_PALETTE.amber,
    EARTHY_PALETTE.terracotta,
    EARTHY_PALETTE.rust
  ];

  riskChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: displayLabels,
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
            font: { size: 12, weight: "bold", family: "'Plus Jakarta Sans', 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif" },
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

  const labels = plots.map(p => {
    const cName = TRANSLATIONS[currentLang]?.crops[p.crop_type] || p.crop_type.replace("_", " ");
    return `${p.plot_id} (${cName})`;
  });
  const allocated = plots.map(p => p.allocated_liters);
  const areas = plots.map(p => p.area_acres);

  const waterBarLabel = TRANSLATIONS[currentLang]?.charts?.alloc_bar_label || "Allocated Water (L)";
  const areaLineLabel = TRANSLATIONS[currentLang]?.charts?.area_line_label || "Field Area (Acres)";

  allocationChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: waterBarLabel,
          data: allocated,
          backgroundColor: "rgba(76, 84, 61, 0.85)",
          borderColor: EARTHY_PALETTE.moss,
          borderWidth: 1,
          borderRadius: 4,
          yAxisID: "y"
        },
        {
          label: areaLineLabel,
          data: areas,
          type: "line",
          borderColor: EARTHY_PALETTE.amber,
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
          ticks: { color: EARTHY_PALETTE.charcoal, font: { size: 11, weight: "600", family: "'Plus Jakarta Sans', 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif" } },
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
          labels: { color: EARTHY_PALETTE.charcoal, font: { size: 11, weight: "bold", family: "'Plus Jakarta Sans', 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif" } }
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
  lastForecastData = forecast;
  lastProjectedMetrics = metrics;

  const tmaxWord = TRANSLATIONS[currentLang]?.charts?.avg_tmax_label || "Avg Temp Max:";
  const rainWord = TRANSLATIONS[currentLang]?.charts?.total_rain_label || "Total Rain (14d):";
  const et0Word = TRANSLATIONS[currentLang]?.charts?.et0_label || "ET0 Demand:";
  const netDeficitWord = currentLang === "te" ? "నికర లోటు:" : (currentLang === "hi" ? "शुद्ध कमी:" : "Water Balance:");

  const pillsWrap = document.getElementById("forecastPills");
  pillsWrap.innerHTML = `
    <span class="f-pill">${tmaxWord} <b>${metrics.avg_future_temp_max}°C</b></span>
    <span class="f-pill">${rainWord} <b>${metrics.sum_future_rainfall_14d} mm</b></span>
    <span class="f-pill">${et0Word} <b>${metrics.sum_future_et0_14d} mm</b></span>
    <span class="f-pill">${netDeficitWord} <b>${metrics.projected_water_balance} mm</b></span>
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

  const tmaxLabel = currentLang === "te" ? "గరిష్ట ఉష్ణోగ్రత (°C)" : (currentLang === "hi" ? "अधिकतम तापमान (°C)" : "Projected Max Temp (°C)");
  const rainLabel = currentLang === "te" ? "వర్షపాతం (మి.మీ)" : (currentLang === "hi" ? "वर्षा (मिमी)" : "Precipitation (mm)");
  const et0Label = currentLang === "te" ? "ET0 బాష్పీభవనం (మి.మీ)" : (currentLang === "hi" ? "ET0 वाष्पोत्सर्जन (मिमी)" : "ET0 Evapotranspiration (mm)");

  forecastChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: tmaxLabel,
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
          label: rainLabel,
          data: rain,
          backgroundColor: "rgba(76, 84, 61, 0.8)",
          borderColor: EARTHY_PALETTE.moss,
          borderWidth: 1,
          yAxisID: "yRain",
          borderRadius: 3
        },
        {
          label: et0Label,
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
          ticks: { color: EARTHY_PALETTE.charcoal, font: { size: 10, family: "'Plus Jakarta Sans', 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif" } },
          grid: { color: "rgba(164, 176, 146, 0.3)" }
        },
        yTemp: {
          type: "linear",
          position: "right",
          title: { display: true, text: "°C", color: EARTHY_PALETTE.terracotta },
          ticks: { color: EARTHY_PALETTE.terracotta },
          grid: { drawOnChartArea: false }
        },
        yRain: {
          type: "linear",
          position: "left",
          title: { display: true, text: "mm", color: EARTHY_PALETTE.moss },
          ticks: { color: EARTHY_PALETTE.moss },
          grid: { color: "rgba(164, 176, 146, 0.3)" }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: EARTHY_PALETTE.charcoal, font: { size: 11, weight: "bold", family: "'Plus Jakarta Sans', 'Noto Sans Telugu', 'Noto Sans Devanagari', sans-serif" } }
        }
      }
    }
  });
}

function renderFutureCropsList(crops) {
  lastFutureCropsData = crops;
  const container = document.getElementById("futureCropsList");
  if (!container) return;
  container.innerHTML = "";

  if (!crops || crops.length === 0) {
    const emptyMsg = currentLang === "te"
      ? "సిఫార్సు చేయడానికి అనువైన పంటలు అందుబాటులో లేవు."
      : (currentLang === "hi" ? "कोई अनुशंसित फसल उपलब्ध नहीं है।" : "No future crop recommendations available.");
    container.innerHTML = `<div class="loading-state">${emptyMsg}</div>`;
    return;
  }

  const fitWord = TRANSLATIONS[currentLang]?.charts?.fit_suffix || "Fit";
  const projCsiWord = TRANSLATIONS[currentLang]?.charts?.proj_csi || "Projected CSI:";
  const riskWord = TRANSLATIONS[currentLang]?.charts?.risk || "Risk:";
  const heatTolWord = TRANSLATIONS[currentLang]?.charts?.heat_tol || "Heat Tol:";

  crops.forEach((c, idx) => {
    const card = document.createElement("div");
    card.className = "crop-card";
    const icon = CROP_ICONS[c.crop_type] || "🌱";
    const badgeClass = (RISK_CONFIG[c.risk_level] || {}).badgeClass || "badge-low";
    const cropLabel = TRANSLATIONS[currentLang]?.crops[c.crop_type] || c.crop_type.replace("_", " ");
    const riskLabel = TRANSLATIONS[currentLang]?.risks[c.risk_level] || c.risk_level;
    const translatedReasoning = translateFutureReasoning(c.reasoning, currentLang);

    card.innerHTML = `
      <div class="crop-card-top">
        <span class="crop-name">${icon} #${idx + 1} ${cropLabel}</span>
        <span class="crop-suitability">${c.suitability_score_pct}% ${fitWord}</span>
      </div>
      <div class="crop-card-metrics">
        <span>${projCsiWord} <b>${c.projected_csi.toFixed(3)}</b></span>
        <span>${riskWord} <span class="badge ${badgeClass}">${riskLabel}</span></span>
        <span>${heatTolWord} <b>${c.temp_tolerance}°C</b></span>
      </div>
      <div class="crop-card-rationale">
        ${translatedReasoning}
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
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}
