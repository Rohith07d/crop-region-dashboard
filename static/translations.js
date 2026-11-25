/**
 * AgriStress — Farmer Water & Crop Allocator
 * Complete Multi-Language Translation Dictionary (English, Telugu, Hindi)
 * 
 * Clean vanilla JavaScript i18n dictionary.
 * CRITICAL: Internal backend keys (crop_type, soil_type, growth_stage, region_name)
 * remain in standard English for model inference. Only display labels are translated.
 */

window.TRANSLATIONS = {
  en: {
    meta: {
      title: "AgriStress — Farmer Water & Crop Allocator",
      subtitle: "Live Open-Meteo Satellite Feed • FAO-56 Stress Modeling • Interactive Field-Level Water Planner",
      footer: "AgriStress Farmer Water & Crop Allocator • Powered by Open-Meteo High-Resolution Satellite Feed & FAO-56 Agronomic Random Forest"
    },
    nav: {
      state_label: "State:",
      cluster_label: "Farm Cluster:",
      browse_clusters: "Browse Clusters",
      sync_weather: "Sync Weather",
      switch_cluster: "Switch Cluster",
      lang_btn: "Language"
    },
    weather: {
      source_live: "Live Open-Meteo Satellite Feed",
      source_cache: "Fallback Database Cache",
      grid_label: "11km ECMWF Grid",
      latency_suffix: "ms latency",
      today: "Today",
      max_min_temp: "Max / Min Temp",
      mean_humidity: "Mean Humidity",
      wind_speed: "Wind Speed",
      solar_radiation: "Solar Radiation",
      rainfall_10d: "Rainfall (10d)",
      et0_demand: "ET0 Demand (10d)",
      satellite_root_soil: "Satellite Root Soil (7-28cm)",
      topsoil_profile: "Topsoil / Profile (0-7 / 28-100cm)",
      cluster_coords: "Cluster GPS Coordinates",
      soil_classification: "Soil Classification",
      db_store: "Database Store",
      ayacut_prefix: "Ayacut: "
    },
    planner: {
      section_num: "01",
      section_title: "Interactive Farmer Water & Field Planner",
      section_desc: "Adjust your available irrigation water volume and configure your field plots to simulate real-time FAO-56 stress and optimal distribution.",
      available_supply_title: "Available Farm Water Supply",
      liters_unit: "Liters",
      source_title: "Primary Water Source",
      source_label: "Source Type:",
      fields_config_title: "Your Farm Plots & Crop Allocation",
      add_plot: "Add Field Plot",
      simulate_btn: "Simulate Field Stress & Optimal Allocation",
      th_plot_id: "Field ID",
      th_crop: "Crop Type",
      th_stage: "Growth Stage",
      th_area: "Area (Acres)",
      th_moisture: "Root Moisture (m³/m³)",
      th_action: "Action",
      btn_remove: "Remove",
      live_satellite: "Live Satellite",
      th_res_priority: "Priority",
      th_res_field: "Field ID",
      th_res_crop: "Crop Type",
      th_res_stage: "Stage",
      th_res_area: "Area",
      th_res_sm: "Root Moisture",
      th_res_csi: "Predicted CSI",
      th_res_risk: "Risk Level",
      th_res_score: "Priority Score",
      th_res_ideal: "Ideal Water Need",
      th_res_allocated: "Allocated Water",
      th_res_depth: "Depth",
      th_res_drivers: "Stress Drivers",
      loading_sim: "Loading simulation...",
      status_surplus: "SUFFICIENT WATER SUPPLY",
      status_deficit: "WATER DEFICIT ALERT",
      stress_met_suffix: "Stress Demand Met"
    },
    kpi: {
      total_area: "Total Monitored Area",
      active_plots: "Active Plots",
      crop_varieties: "Crop Varieties",
      avg_csi: "Average Stress Index (CSI)",
      acres_unit: "Acres",
      plots_unit: "Plots",
      varieties_unit: "crop types"
    },
    charts: {
      sec2_title: "14-Day Weather Forecast & Next-Season Suitable Crops",
      sec2_desc: "Open-Meteo numerical climate projection and model-evaluated optimal crops for the cluster's soil and upcoming temperatures.",
      stress_dist_title: "Field Stress Risk Distribution",
      stress_dist_sub: "Plot breakdown by FAO-56 critical threshold classification",
      alloc_chart_title: "Water Allocation by Farmer Crop",
      alloc_chart_sub: "Optimized distribution (Liters) vs Field Area (Acres)",
      alloc_bar_label: "Allocated Water (L)",
      area_line_label: "Field Area (Acres)",
      forecast_title: "Cluster 14-Day Climate Forecast",
      forecast_sub: "Daily Projected Max Temperature (°C), Precipitation (mm), and ET0 (mm)",
      future_crops_title: "Top 5 Recommended Crops",
      future_crops_sub: "Agronomically simulated for this cluster's soil & climate",
      avg_tmax_label: "Avg Temp Max:",
      total_rain_label: "Total Rain (14d):",
      et0_label: "ET0 Demand:",
      fit_suffix: "Fit",
      proj_csi: "Projected CSI:",
      risk: "Risk:",
      heat_tol: "Heat Tol:",
      evaluating_crops: "Evaluating next-season crop suitability..."
    },
    modal: {
      welcome_badge: "🌾 Regional Agronomic Intelligence",
      welcome_title: "Welcome to AgriStress",
      welcome_sub: "Choose your preferred language for interactive farm water & crop planning • మీ ప్రాధాన్య భాషను ఎంచుకోండి • अपनी पसंदीदा भाषा चुनें",
      en_title: "English",
      en_sub: "Standard English",
      en_desc: "Interactive FAO-56 stress modeling, water budgeting, and cluster satellite intelligence in English.",
      en_btn: "Continue in English",
      te_title: "తెలుగు (Telugu)",
      te_sub: "ఆంధ్రప్రదేశ్ & తెలంగాణ",
      te_desc: "తెలంగాణ మరియు ఆంధ్రప్రదేశ్ రైతులకు అనుకూలమైన తెలుగు భాషలో సాగునీటి కేటాయింపు మరియు పంట రక్షణ సలహాలు.",
      te_btn: "తెలుగులో కొనసాగండి",
      hi_title: "हिन्दी (Hindi)",
      hi_sub: "राष्ट्रीय कृषि मंच",
      hi_desc: "फसल जल तनाव सूचकांक, मौसम पूर्वानुमान और खेत-स्तरीय सिंचाई जल आवंटन की पूरी जानकारी हिन्दी में।",
      hi_btn: "हिन्दी में जारी रखें",
      clusters_title: "Select Farm Cluster",
      clusters_sub: "Choose from 8 localized agricultural clusters in Telangana and Andhra Pradesh",
      tab_all: "All Clusters (8)",
      tab_ts: "Telangana (4)",
      tab_ap: "Andhra Pradesh (4)",
      active_badge: "✓ Active",
      soil_label: "Soil:",
      gps_label: "GPS:"
    },
    crops: {
      Rice: "Rice",
      Cotton: "Cotton",
      Maize: "Maize",
      Soybean: "Soybean",
      Groundnut: "Groundnut",
      Chilli_Export: "Chilli Export",
      Turmeric: "Turmeric",
      Gherkins: "Gherkins",
      Dragon_Fruit: "Dragon Fruit",
      Pomegranate: "Pomegranate",
      Avocado: "Avocado",
      Quinoa: "Quinoa",
      Bell_Pepper: "Bell Pepper",
      Guava_Export: "Guava Export",
      Okra_Export: "Okra Export",
      Wheat: "Wheat",
      Sugarcane: "Sugarcane",
      Chilli: "Chilli",
      Sorghum: "Sorghum",
      Pearl_Millet: "Pearl Millet",
      Pigeon_Pea: "Pigeon Pea",
      Chickpea: "Chickpea",
      Sunflower: "Sunflower",
      Tomato: "Tomato"
    },
    risks: {
      Low: "Low",
      Moderate: "Moderate",
      High: "High",
      Critical: "Critical"
    },
    soils: {
      Black_Clay: "Black Clay",
      Red_Sandy: "Red Sandy",
      Alluvial_Loam: "Alluvial Loam"
    },
    stages: {
      Initial: "Initial Stage",
      Development: "Development Stage",
      Mid_Season: "Mid Season",
      Late_Season: "Late Season"
    },
    sources: {
      Borewell: "Borewell",
      "Canal Lift": "Canal Lift",
      "Farm Pond": "Farm Pond",
      "Open Well": "Open Well"
    },
    states: {
      all: "All States",
      Telangana: "Telangana",
      "Andhra Pradesh": "Andhra Pradesh"
    }
  },

  te: {
    meta: {
      title: "అగ్రిస్ట్రెస్ — రైతు నీటి & పంట కేటాయింపు సాధనం",
      subtitle: "ప్రత్యక్ష ఓపెన్-మెటియో ఉపగ్రహ సమాచారం • FAO-56 ఒత్తిడి మోడలింగ్ • పొలాల వారీ నీటి ప్రణాళిక",
      footer: "అగ్రిస్ట్రెస్ రైతు నీటి & పంట కేటాయింపు సాధనం • ఓపెన్-మెటియో హై-రిజల్యూషన్ శాటిలైట్ ఫీడ్ మరియు FAO-56 రాండమ్ ఫారెస్ట్ మోడల్ ద్వారా ఆధారితం"
    },
    nav: {
      state_label: "రాష్ట్రం:",
      cluster_label: "రైతు క్లస్టర్:",
      browse_clusters: "క్లస్టర్ల వివరాలు",
      sync_weather: "వాతావరణం రీఫ్రెష్",
      switch_cluster: "క్లస్టర్ మార్చండి",
      lang_btn: "భాష"
    },
    weather: {
      source_live: "ప్రత్యక్ష ఓపెన్-మెటియో ఉపగ్రహ సమాచారం",
      source_cache: "డేటాబేస్ నిల్వ సమాచారం",
      grid_label: "11కి.మీ ECMWF గ్రిడ్",
      latency_suffix: "మి.సె ఆలస్యం",
      today: "ఈరోజు",
      max_min_temp: "గరిష్ట / కనిష్ట ఉష్ణోగ్రత",
      mean_humidity: "సగటు తేమ శాతం",
      wind_speed: "గాలి వేగం",
      solar_radiation: "సౌర వికిరణం",
      rainfall_10d: "గత 10 రోజుల వర్షపాతం",
      et0_demand: "ఆవిరి డిమాండ్ (ET0 10 రోజులు)",
      satellite_root_soil: "ఉపగ్రహ వేరు నేల తేమ (7-28 సెం.మీ)",
      topsoil_profile: "ఉపరితల / లోపలి తేమ (0-7 / 28-100 సెం.మీ)",
      cluster_coords: "క్లస్టర్ GPS అక్షాంశ-రేఖాంశాలు",
      soil_classification: "నేల రకం వర్గీకరణ",
      db_store: "డేటాబేస్ నిల్వ రకం",
      ayacut_prefix: "ఆయకట్టు: "
    },
    planner: {
      section_num: "01",
      section_title: "రైతు నీటి కేటాయింపు & పొలాల ప్రణాళికా సాధనం",
      section_desc: "మీ వద్ద ఉన్న సాగునీటి పరిమాణాన్ని నమోదు చేసి, పొలాల వివరాలను మార్చుతూ నిజ-సమయ FAO-56 పంట ఒత్తిడి మరియు సరైన నీటి పంపిణీని లెక్కించండి.",
      available_supply_title: "అందుబాటులో ఉన్న సాగునీరు",
      liters_unit: "లీటర్లు",
      source_title: "ప్రధాన నీటి వనరు",
      source_label: "వనరు రకం:",
      fields_config_title: "మీ పొలాల వివరాలు & పంట నమోదు",
      add_plot: "పొలాన్ని చేర్చండి ➕",
      simulate_btn: "పంట ఒత్తిడి & సరైన నీటి పంపకాన్ని లెక్కించండి ⚡",
      th_plot_id: "పొలం సంఖ్య",
      th_crop: "పంట రకం",
      th_stage: "ఎదుగుదల దశ",
      th_area: "విస్తీర్ణం (ఎకరాలు)",
      th_moisture: "వేరు నేల తేమ (m³/m³)",
      th_action: "చర్య",
      btn_remove: "తొలగించు",
      live_satellite: "ఉపగ్రహ ప్రత్యక్ష తేమ",
      th_res_priority: "ప్రాధాన్యత",
      th_res_field: "పొలం ఐడీ",
      th_res_crop: "పంట",
      th_res_stage: "దశ",
      th_res_area: "విస్తీర్ణం",
      th_res_sm: "నేల తేమ",
      th_res_csi: "అంచనా వేసిన CSI",
      th_res_risk: "ప్రమాద స్థాయి",
      th_res_score: "ప్రాధాన్యతా స్కోరు",
      th_res_ideal: "అవసరమైన నీరు",
      th_res_allocated: "కేటాయించిన నీరు",
      th_res_depth: "నీటి లోతు",
      th_res_drivers: "ఒత్తిడికి ప్రధాన కారణాలు",
      loading_sim: "లెక్కలు వేస్తోంది...",
      status_surplus: "తగినంత నీటి నిల్వ ఉంది",
      status_deficit: "నీటి కొరత హెచ్చరిక",
      stress_met_suffix: "ఒత్తిడి అవసరం తీరింది"
    },
    kpi: {
      total_area: "మొత్తం పర్యవేక్షణ విస్తీర్ణం",
      active_plots: "నమోదైన పొలాలు",
      crop_varieties: "పంటల రకాలు",
      avg_csi: "సగటు పంట ఒత్తిడి సూచిక (CSI)",
      acres_unit: "ఎకరాలు",
      plots_unit: "పొలాలు",
      varieties_unit: "రకాల పంటలు"
    },
    charts: {
      sec2_title: "14-రోజుల వాతావరణ అంచనా & తదుపరి సీజన్ అనుకూల పంటలు",
      sec2_desc: "ఓపెన్-మెటియో వాతావరణ అంచనా మరియు ఈ క్లస్టర్ నేల, ఉష్ణోగ్రతలకు అనుగుణంగా మోడల్ సిఫార్సు చేసిన ఉత్తమ పంటలు.",
      stress_dist_title: "పొలాల పంట ఒత్తిడి ప్రమాద విభజన",
      stress_dist_sub: "FAO-56 ప్రమాద స్థాయిల ప్రకారం పొలాల వర్గీకరణ",
      alloc_chart_title: "పంటల వారీగా నీటి కేటాయింపు",
      alloc_chart_sub: "కేటాయించిన నీరు (లీటర్లు) మరియు పొలం విస్తీర్ణం (ఎకరాలు)",
      alloc_bar_label: "కేటాయించిన నీరు (లీటర్లు)",
      area_line_label: "పొలం విస్తీర్ణం (ఎకరాలు)",
      forecast_title: "క్లస్టర్ 14 రోజుల వాతావరణ అంచనా",
      forecast_sub: "రోజువారీ గరిష్ట ఉష్ణోగ్రత (°C), వర్షపాతం (మి.మీ), మరియు బాష్పీభవనం ET0 (మి.మీ)",
      future_crops_title: "రాబోయే కాలానికి టాప్ 5 అనుకూల పంటలు",
      future_crops_sub: "ఈ ప్రాంత నేల మరియు వాతావరణానికి శాస్త్రీయంగా సిఫార్సు చేసిన పంటలు",
      avg_tmax_label: "సగటు గరిష్ట ఉష్ణోగ్రత:",
      total_rain_label: "14 రోజుల మొత్తం వర్షం:",
      et0_label: "మొత్తం ET0 డిమాండ్:",
      fit_suffix: "అనుకూలత",
      proj_csi: "అంచనా CSI:",
      risk: "ప్రమాదం:",
      heat_tol: "ఉష్ణ నిరోధకత:",
      evaluating_crops: "అనుకూల పంటలను విశ్లేషిస్తోంది..."
    },
    modal: {
      welcome_badge: "🌾 ప్రాంతీయ వ్యవసాయ మరియు సాగునీటి వేదిక",
      welcome_title: "అగ్రిస్ట్రెస్ కు స్వాగతం",
      welcome_sub: "మీ పొలాల సాగునీటి ప్రణాళిక కోసం మీకు అనుకూలమైన భాషను ఎంచుకోండి:",
      en_title: "English (ఆంగ్లం)",
      en_sub: "Standard English",
      en_desc: "FAO-56 పంట ఒత్తిడి విశ్లేషణ మరియు ఉపగ్రహ ఆధారిత వాతావరణ ప్రణాళిక ఆంగ్లంలో.",
      en_btn: "Continue in English",
      te_title: "తెలుగు (Telugu)",
      te_sub: "ఆంధ్రప్రదేశ్ & తెలంగాణ రైతుల కోసం",
      te_desc: "మన నేలలు మరియు వాతావరణానికి అనువైన పంటలు, సరైన నీటి పంపకం వివరాలు సూటిగా తెలుగులో.",
      te_btn: "తెలుగులో కొనసాగండి",
      hi_title: "हिन्दी (Hindi)",
      hi_sub: "हिन्दी भाषी किसानों के लिए",
      hi_desc: "फसल जल तनाव, मौसम पूर्वानुमान और खेत-स्तरीय सिंचाई आवंटन की संपूर्ण जानकारी हिन्दी में।",
      hi_btn: "हिन्दी में जारी रखें",
      clusters_title: "వ్యవసాయ క్లస్టర్‌ను ఎంచుకోండి",
      clusters_sub: "తెలంగాణ మరియు ఆంధ్రప్రదేశ్‌లోని 8 గ్రామీణ వ్యవసాయ క్లస్టర్ల నుండి ఎంచుకోండి",
      tab_all: "అన్ని క్లస్టర్లు (8)",
      tab_ts: "తెలంగాణ (4)",
      tab_ap: "ఆంధ్రప్రదేశ్ (4)",
      active_badge: "✓ ప్రస్తుతం క్రియాశీలం",
      soil_label: "నేల రకం:",
      gps_label: "GPS:"
    },
    crops: {
      Rice: "వరి",
      Cotton: "పత్తి",
      Maize: "మొక్కజొన్న",
      Soybean: "సోయాబీన్",
      Groundnut: "వేరుశెనగ",
      Chilli_Export: "మిరప (ఎగుమతి)",
      Turmeric: "పసుపు",
      Gherkins: "దోసకాయలు (ఘెర్కిన్స్)",
      Dragon_Fruit: "డ్రాగన్ ఫ్రూట్",
      Pomegranate: "దానిమ్మ",
      Avocado: "అవకాడో",
      Quinoa: "క్వినోవా",
      Bell_Pepper: "క్యాప్సికం (బెల్ పెప్పర్)",
      Guava_Export: "జామ (ఎగుమతి)",
      Okra_Export: "బెండకాయ (ఎగుమతి)",
      Wheat: "గోధుమ",
      Sugarcane: "చెరకు",
      Chilli: "మిరప",
      Sorghum: "జొన్న",
      Pearl_Millet: "సజ్జలు",
      Pigeon_Pea: "కందులు",
      Chickpea: "శనగలు",
      Sunflower: "పొద్దుతిరుగుడు",
      Tomato: "టమాటా"
    },
    risks: {
      Low: "అల్ప ప్రమాదం",
      Moderate: "మధ్యస్థం",
      High: "అధిక ప్రమాదం",
      Critical: "తీవ్రమైన ప్రమాదం"
    },
    soils: {
      Black_Clay: "నల్లరేగడి నేల",
      Red_Sandy: "ఎర్ర ఇసుక నేల",
      Alluvial_Loam: "ఒండ్రు నేల"
    },
    stages: {
      Initial: "ప్రారంభ దశ",
      Development: "ఎదుగుదల దశ",
      Mid_Season: "మధ్య దశ (కీలకం)",
      Late_Season: "ముగింపు దశ"
    },
    sources: {
      Borewell: "బోరుబావి",
      "Canal Lift": "కాలువ లిఫ్ట్",
      "Farm Pond": "రైతు కుంట / చెరువు",
      "Open Well": "బావి"
    },
    states: {
      all: "అన్ని రాష్ట్రాలు",
      Telangana: "తెలంగాణ",
      "Andhra Pradesh": "ఆంధ్రప్రదేశ్"
    }
  },

  hi: {
    meta: {
      title: "एग्रीस्ट्रेस — किसान जल एवं फसल आवंटन उपकरण",
      subtitle: "लाइव ओपन-मेटियो उपग्रह डेटा • FAO-56 तनाव मॉडलिंग • इंटरैक्टिव खेत-स्तरीय जल योजनाकार",
      footer: "एग्रीस्ट्रेस किसान जल एवं फसल आवंटन उपकरण • ओपन-मेटियो उच्च-रिज़ॉल्यूशन उपग्रह फ़ीड एवं FAO-56 रैंडम फ़ॉरेस्ट मॉडल द्वारा संचालित"
    },
    nav: {
      state_label: "राज्य:",
      cluster_label: "कृषि क्लस्टर:",
      browse_clusters: "सभी क्लस्टर देखें",
      sync_weather: "मौसम रीफ़्रेश करें",
      switch_cluster: "क्लस्टर बदलें",
      lang_btn: "भाषा"
    },
    weather: {
      source_live: "लाइव ओपन-मेटियो उपग्रह डेटा",
      source_cache: "डेटाबेस सुरक्षित डेटा",
      grid_label: "11 किमी ECMWF ग्रिड",
      latency_suffix: "मिलीसेकंड विलंब",
      today: "आज",
      max_min_temp: "अधिकतम / न्यूनतम तापमान",
      mean_humidity: "औसत आर्द्रता",
      wind_speed: "हवा की गति",
      solar_radiation: "सौर विकिरण",
      rainfall_10d: "पिछले 10 दिनों की वर्षा",
      et0_demand: "वाष्पीकरण मांग (ET0 10 दिन)",
      satellite_root_soil: "उपग्रह जड़ क्षेत्र नमी (7-28 सेमी)",
      topsoil_profile: "सतह / गहरी नमी (0-7 / 28-100 सेमी)",
      cluster_coords: "क्लस्टर जीपीएस निर्देशांक",
      soil_classification: "मिट्टी का वर्गीकरण",
      db_store: "डेटाबेस स्टोरेज प्रकार",
      ayacut_prefix: "कमांड क्षेत्र: "
    },
    planner: {
      section_num: "01",
      section_title: "इंटरैक्टिव किसान जल एवं खेत योजनाकार",
      section_desc: "अपने उपलब्ध सिंचाई जल की मात्रा निर्धारित करें और वास्तविक समय FAO-56 फसल तनाव और इष्टतम जल वितरण का अनुकरण करें।",
      available_supply_title: "उपलब्ध सिंचाई जल आपूर्ति",
      liters_unit: "लीटर",
      source_title: "प्रमुख जल स्रोत",
      source_label: "स्रोत प्रकार:",
      fields_config_title: "आपके खेत के भूखंड एवं फसल विन्यास",
      add_plot: "खेत जोड़ें ➕",
      simulate_btn: "फसल तनाव एवं इष्टतम जल आवंटन अनुकरण करें ⚡",
      th_plot_id: "खेत पहचान संख्या",
      th_crop: "फसल प्रकार",
      th_stage: "विकास अवस्था",
      th_area: "क्षेत्रफल (एकड़)",
      th_moisture: "जड़ क्षेत्र नमी (m³/m³)",
      th_action: "कार्रवाई",
      btn_remove: "हटाएं",
      live_satellite: "लाइव उपग्रह नमी",
      th_res_priority: "प्राथमिकता",
      th_res_field: "खेत आईडी",
      th_res_crop: "फसल",
      th_res_stage: "अवस्था",
      th_res_area: "क्षेत्रफल",
      th_res_sm: "जड़ नमी",
      th_res_csi: "अनुमानित CSI",
      th_res_risk: "जोखिम स्तर",
      th_res_score: "प्राथमिकता स्कोर",
      th_res_ideal: "आदर्श जल आवश्यकता",
      th_res_allocated: "आवंटित जल",
      th_res_depth: "जल गहराई",
      th_res_drivers: "तनाव के मुख्य कारक",
      loading_sim: "गणना जारी है...",
      status_surplus: "पर्याप्त जल भंडार उपलब्ध है",
      status_deficit: "जल की कमी की चेतावनी",
      stress_met_suffix: "तनाव आवश्यकता पूरी हुई"
    },
    kpi: {
      total_area: "कुल निगरानी क्षेत्र",
      active_plots: "सक्रिय खेत",
      crop_varieties: "फसल किस्में",
      avg_csi: "औसत फसल तनाव सूचकांक (CSI)",
      acres_unit: "एकड़",
      plots_unit: "खेत",
      varieties_unit: "फसल किस्में"
    },
    charts: {
      sec2_title: "14-दिवसीय मौसम पूर्वानुमान एवं आगामी सीजन हेतु उपयुक्त फसलें",
      sec2_desc: "ओपन-मेटियो जलवायु पूर्वानुमान और इस क्लस्टर की मिट्टी व आगामी तापमान के अनुसार मॉडल द्वारा अनुशंसित सर्वोत्तम फसलें।",
      stress_dist_title: "खेत फसल तनाव जोखिम वितरण",
      stress_dist_sub: "FAO-56 क्रांतिक सीमा वर्गीकरण के आधार पर खेतों का विभाजन",
      alloc_chart_title: "फसलवार सिंचाई जल आवंटन",
      alloc_chart_sub: "इष्टतम जल आवंटन (लीटर) बनाम खेत क्षेत्रफल (एकड़)",
      alloc_bar_label: "आवंटित जल (लीटर)",
      area_line_label: "खेत क्षेत्रफल (एकड़)",
      forecast_title: "क्लस्टर 14-दिवसीय मौसम पूर्वानुमान",
      forecast_sub: "दैनिक अधिकतम तापमान (°C), वर्षा (मिमी), और वाष्पोत्सर्जन ET0 (मिमी)",
      future_crops_title: "आगामी मौसम हेतु शीर्ष 5 अनुशंसित फसलें",
      future_crops_sub: "इस क्षेत्र की मिट्टी और जलवायु के अनुकूल कृषि वैज्ञानिक सिफारिशें",
      avg_tmax_label: "औसत अधि. तापमान:",
      total_rain_label: "14-दिन कुल वर्षा:",
      et0_label: "कुल ET0 मांग:",
      fit_suffix: "उपयुक्तता",
      proj_csi: "अनुमानित CSI:",
      risk: "जोखिम:",
      heat_tol: "ताप सहनशीलता:",
      evaluating_crops: "अनुकूल फसलों का मूल्यांकन जारी है..."
    },
    modal: {
      welcome_badge: "🌾 क्षेत्रीय कृषि एवं जल बुद्धिमत्ता",
      welcome_title: "एग्रीस्ट्रेस में आपका स्वागत है",
      welcome_sub: "इंटरैक्टिव फसल जल योजना जारी रखने के लिए अपनी पसंदीदा भाषा चुनें:",
      en_title: "English (अंग्रेजी)",
      en_sub: "Standard English",
      en_desc: "FAO-56 तनाव मॉडलिंग, जल बजट और उपग्रह मौसम जानकारी अंग्रेजी में देखें।",
      en_btn: "Continue in English",
      te_title: "తెలుగు (Telugu)",
      te_sub: "ఆంధ్రప్రదేశ్ & తెలంగాణ రైతుల కోసం",
      te_desc: "ఆంధ్రప్రదేశ్ మరియు తెలంగాణ రైతుల కోసం తెలుగులో సాగునీటి ప్రణాళిక మరియు పంట సలహాలు.",
      te_btn: "తెలుగులో కొనసాగండి",
      hi_title: "हिन्दी (Hindi)",
      hi_sub: "सभी हिन्दी भाषी क्षेत्रों के लिए",
      hi_desc: "फसल जल तनाव प्रबंधन, वास्तविक समय उपग्रह मौसम और प्राथमिक सिंचाई आवंटन हिन्दी में।",
      hi_btn: "हिन्दी में जारी रखें",
      clusters_title: "कृषि क्लस्टर चुनें",
      clusters_sub: "तेलंगाना और आंध्र प्रदेश के 8 स्थानीय कृषि क्षेत्रों में से चयन करें",
      tab_all: "सभी क्लस्टर (8)",
      tab_ts: "तेलंगाना (4)",
      tab_ap: "आंध्र प्रदेश (4)",
      active_badge: "✓ सक्रिय",
      soil_label: "मिट्टी:",
      gps_label: "जीपीएस:"
    },
    crops: {
      Rice: "धान",
      Cotton: "कपास",
      Maize: "मक्का",
      Soybean: "सोयाबीन",
      Groundnut: "मूंगफली",
      Chilli_Export: "मिर्च (निर्यात)",
      Turmeric: "हल्दी",
      Gherkins: "खीरा (घेरकिन्स)",
      Dragon_Fruit: "ड्रैगन फ्रूट",
      Pomegranate: "अनार",
      Avocado: "एवोकैडो",
      Quinoa: "क्विनोआ",
      Bell_Pepper: "शिमला मिर्च",
      Guava_Export: "अमरूद (निर्यात)",
      Okra_Export: "भिंडी (निर्यात)",
      Wheat: "गेहूं",
      Sugarcane: "गन्ना",
      Chilli: "मिर्च",
      Sorghum: "ज्वार",
      Pearl_Millet: "बाजरा",
      Pigeon_Pea: "अरहर",
      Chickpea: "चना",
      Sunflower: "सूरजमुखी",
      Tomato: "टमाटर"
    },
    risks: {
      Low: "कम जोखिम",
      Moderate: "मध्यम",
      High: "उच्च जोखिम",
      Critical: "गंभीर जोखिम"
    },
    soils: {
      Black_Clay: "काली मिट्टी",
      Red_Sandy: "लाल रेतीली मिट्टी",
      Alluvial_Loam: "जलोढ़ दोमट मिट्टी"
    },
    stages: {
      Initial: "प्रारंभिक अवस्था",
      Development: "विकास अवस्था",
      Mid_Season: "मध्य मौसम (महत्वपूर्ण)",
      Late_Season: "अंतिम अवस्था"
    },
    sources: {
      Borewell: "बोरवेल",
      "Canal Lift": "नहर लिफ्ट",
      "Farm Pond": "खेत तालाब",
      "Open Well": "खुला कुआं"
    },
    states: {
      all: "सभी राज्य",
      Telangana: "तेलंगाना",
      "Andhra Pradesh": "आंध्र प्रदेश"
    }
  }
};

/**
 * Natural language agricultural translation helpers for dynamic model explanations
 */
function translateStressDriver(driverText, lang = "en") {
  if (!driverText) return "";
  if (lang === "en") return driverText;

  // Patterns from app.py run_model_inference
  // 1. Root moisture severely below threshold
  const mSevere = driverText.match(/Root moisture severely below threshold by ([\d.]+)/);
  if (mSevere) {
    const val = mSevere[1];
    return lang === "te" 
      ? `వేరు తేమ కీలక స్థాయి కంటే తీవ్రంగా ${val} m³/m³ తక్కువగా ఉంది`
      : `जड़ क्षेत्र की नमी क्रांतिक सीमा से अत्यधिक कम (${val} m³/m³) है`;
  }

  // 2. Root moisture below critical limit
  const mCrit = driverText.match(/Root moisture below critical limit \(([\d.]+)\)/);
  if (mCrit) {
    const val = mCrit[1];
    return lang === "te"
      ? `వేరు ప్రాంతపు నేల తేమ అవసరమైన పరిమితి కంటే తక్కువగా (${val}) ఉంది`
      : `जड़ क्षेत्र की नमी आवश्यक सीमा से कम (${val}) है`;
  }

  // 3. Severe thermal stress
  const mHeatSev = driverText.match(/Severe thermal stress \(\+([\d.]+)°C above tolerance\)/);
  if (mHeatSev) {
    const val = mHeatSev[1];
    return lang === "te"
      ? `అధిక వేడి ఒత్తిడి (పంట తట్టుకునే స్థాయి కంటే +${val}°C అధికం)`
      : `गंभीर ताप तनाव (सहनशीलता से +${val}°C अधिक)`;
  }

  // 4. Mild heat excess
  const mHeatMild = driverText.match(/Mild heat excess \(\+([\d.]+)°C\)/);
  if (mHeatMild) {
    const val = mHeatMild[1];
    return lang === "te"
      ? `స్వల్ప వేడి పెరుగుదల (+${val}°C అధికం)`
      : `हल्की गर्मी की अधिकता (+${val}°C)`;
  }

  // 5. High atmospheric drying demand (VPD ...)
  const mVpd = driverText.match(/High atmospheric drying demand \(VPD ([\d.]+) kPa\)/);
  if (mVpd) {
    const val = mVpd[1];
    return lang === "te"
      ? `వాతావరణంలో పొడి గాలి తీవ్రత అధికం (VPD ${val} kPa)`
      : `वायुमंडलीय शुष्कता का अधिक प्रभाव (VPD ${val} kPa)`;
  }

  // 6. 10d net moisture deficit
  const mDef = driverText.match(/10d net moisture deficit \(([-]?[\d.]+) mm\)/);
  if (mDef) {
    const val = mDef[1];
    return lang === "te"
      ? `గత 10 రోజులుగా నికర తేమ లోటు (${val} మి.మీ)`
      : `पिछले 10 दिनों में शुद्ध नमी की कमी (${val} मिमी)`;
  }

  // 7. Optimal physiological & moisture conditions
  if (driverText.includes("Optimal physiological")) {
    return lang === "te"
      ? "అనుకూలమైన తేమ మరియు ఆరోగ్యకరమైన వాతావరణ పరిస్థితులు"
      : "उत्कृष्ट नमी और स्वस्थ शारीरिक परिस्थितियां";
  }

  return driverText;
}

function translateFutureReasoning(reasoningText, lang = "en") {
  if (!reasoningText) return "";
  if (lang === "en") return reasoningText;

  const parts = reasoningText.split(" • ");
  const translatedParts = parts.map(part => {
    // 1. High thermal tolerance
    const mTol = part.match(/High thermal tolerance \((\d+)°C > forecast ([\d.]+)°C\)/);
    if (mTol) {
      return lang === "te"
        ? `మంచి ఉష్ణ నిరోధకత (${mTol[1]}°C > అంచనా ${mTol[2]}°C)`
        : `उच्च ताप सहनशीलता (${mTol[1]}°C > पूर्वानुमान ${mTol[2]}°C)`;
    }

    // 2. Sensitive to projected heat
    const mSens = part.match(/Sensitive to projected heat \(\+([\d.]+)°C excess\)/);
    if (mSens) {
      return lang === "te"
        ? `అంచనా వేసిన వేడికి సున్నితం (+${mSens[1]}°C అధికం)`
        : `अनुमानित गर्मी के प्रति संवेदनशील (+${mSens[1]}°C अधिक)`;
    }

    // 3. Matches soil water capacity
    const mSoil = part.match(/Matches soil water capacity \(([^)]+)\)/);
    if (mSoil) {
      const sName = TRANSLATIONS[lang]?.soils[mSoil[1]] || mSoil[1];
      return lang === "te"
        ? `నేల నీటి నిల్వ సామర్థ్యానికి సరిపోతుంది (${sName})`
        : `मिट्टी की जल संचयन क्षमता के अनुकूल (${sName})`;
    }

    // 4. Requires supplemental irrigation
    const mIrr = part.match(/Requires supplemental irrigation \(crit moisture ([\d.]+)\)/);
    if (mIrr) {
      return lang === "te"
        ? `అదనపు సాగునీరు అవసరం (కీలక తేమ ${mIrr[1]})`
        : `अतिरिक्त सिंचाई की आवश्यकता (महत्वपूर्ण नमी ${mIrr[1]})`;
    }

    return part;
  });

  return translatedParts.join(" • ");
}

function generateFeedbackMessage(waterStatus, availWater, balanceLiters, coveragePct, lang = "en") {
  const fAvail = Number(availWater).toLocaleString("en-US", { maximumFractionDigits: 0 });
  const fBal = Math.abs(Number(balanceLiters)).toLocaleString("en-US", { maximumFractionDigits: 0 });

  if (waterStatus === "SURPLUS") {
    if (lang === "te") {
      return `తగినంత నీటి నిల్వ: మీ వద్ద అందుబాటులో ఉన్న ${fAvail} లీటర్ల నీరు పంట ఒత్తిడి అవసరాలను 100% తీరుస్తుంది మరియు +${fBal} లీటర్ల మిగులు ఉంది.`;
    } else if (lang === "hi") {
      return `पर्याप्त जल भंडार: आपकी उपलब्ध ${fAvail} लीटर आपूर्ति फसलों की 100% तनाव जल आवश्यकता को पूरा करती है और +${fBal} लीटर अतिरिक्त अधिशेष है।`;
    }
    return `Sufficient Water Reserve: Your available supply of ${fAvail} L covers 100% of crop physiological stress requirements with a surplus of +${fBal} L.`;
  } else {
    if (lang === "te") {
      return `నీటి కొరత హెచ్చరిక: అందుబాటులో ఉన్న నీరు ${coveragePct}% ఒత్తిడి అవసరాన్ని మాత్రమే తీరుస్తుంది (${fBal} లీటర్ల కొరత). తీవ్రమైన మరియు అత్యవసర పొలాలకు ప్రాధాన్యత ఇవ్వబడింది.`;
    } else if (lang === "hi") {
      return `जल की कमी की चेतावनी: उपलब्ध पानी केवल ${coveragePct}% आवश्यकता को पूरा करता है (${fBal} लीटर की कमी)। गंभीर और उच्च जोखिम वाले खेतों को प्राथमिकता दी गई है।`;
    }
    return `Water Deficit Warning: Available water covers ${coveragePct}% of stress demand (${fBal} L deficit). Water is prioritized for critical & high-risk plots.`;
  }
}

// Global Exports
window.translateStressDriver = translateStressDriver;
window.translateFutureReasoning = translateFutureReasoning;
window.generateFeedbackMessage = generateFeedbackMessage;
