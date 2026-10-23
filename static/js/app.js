/**
 * AeroGuard AI - Client Application Logic
 * Integrates REST API endpoints, Chart.js visualizations, and dynamic UI state.
 */

let currentStandard = "CPCB";
let currentCity = "Panipat";
let currentData = null;

// Chart Instances
let trendChartInstance = null;
let radarChartInstance = null;
let cityChartInstance = null;
let importanceChartInstance = null;

// Debounce timer for what-if simulator
let simulatorTimer = null;

// Initial application bootstrap
document.addEventListener("DOMContentLoaded", () => {
  fetchCityAQI();
  loadHistoricalData();
  loadModelMetrics();
});

function setStandard(std) {
  currentStandard = std;
  const cpcbBtn = document.getElementById("stdCpcbBtn");
  const epaBtn = document.getElementById("stdEpaBtn");

  if (std === "CPCB") {
    cpcbBtn.className = "px-3 py-1.5 rounded-lg bg-white text-blue-600 shadow-sm transition-all";
    epaBtn.className = "px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all";
  } else {
    epaBtn.className = "px-3 py-1.5 rounded-lg bg-white text-blue-600 shadow-sm transition-all";
    cpcbBtn.className = "px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all";
  }

  fetchCityAQI();
}

function quickSelectCity(name) {
  document.getElementById("cityInput").value = name;
  fetchCityAQI();
}

async function fetchCityAQI() {
  const cityInput = document.getElementById("cityInput").value.trim() || "Panipat";
  const activityInput = document.getElementById("activityInput").value.trim() || "outdoor running";
  const searchBtn = document.getElementById("searchBtn");

  searchBtn.disabled = true;
  searchBtn.innerHTML = `<span class="animate-spin inline-block mr-1">⌛</span> Loading...`;

  try {
    const res = await fetch(`/api/live?city=${encodeURIComponent(cityInput)}&standard=${currentStandard}&activity=${encodeURIComponent(activityInput)}`);
    if (!res.ok) throw new Error("Failed to fetch air quality data");
    const data = await res.json();
    currentData = data;
    currentCity = data.city;

    updateDashboard(data);
  } catch (err) {
    console.error("Fetch error:", err);
    alert("Unable to fetch data for this station. Please check the city name.");
  } finally {
    searchBtn.disabled = false;
    searchBtn.innerHTML = `<i data-lucide="search" class="w-4 h-4"></i> Search`;
    lucide.createIcons();
  }
}

function updateDashboard(data) {
  // 1. Text & Location
  document.getElementById("displayCity").textContent = data.city;
  document.getElementById("displayCountry").textContent = data.country || "Station Telemetry";
  document.getElementById("dataSourceLabel").innerHTML = `
    <span class="w-2 h-2 rounded-full ${data.source === 'live_open_meteo' ? 'bg-emerald-500' : 'bg-blue-500'} animate-pulse"></span>
    ${data.source === 'live_open_meteo' ? 'Live Atmospheric Sensor Feed' : 'Trained Atmospheric Engine'}
  `;

  // 2. AQI Number & Category
  const aqi = data.aqi;
  const catInfo = data.category_info || {};
  const catName = catInfo.category || "Moderate";
  const catColor = catInfo.color || "#f59e0b";

  document.getElementById("displayAQI").textContent = aqi;
  const categoryBadge = document.getElementById("categoryBadge");
  categoryBadge.textContent = catName;
  categoryBadge.style.backgroundColor = catColor;

  const dominantBadge = document.getElementById("dominantBadge");
  dominantBadge.textContent = `${data.dominant_pollutant || "PM2.5"} Dominant`;

  // Circular Gauge Stroke (Circumference = 2 * PI * 80 ≈ 502.65)
  const maxAQI = 500;
  const circumference = 502.65;
  const clampedAQI = Math.min(Math.max(aqi, 0), maxAQI);
  const offset = circumference - (clampedAQI / maxAQI) * circumference;
  
  const gaugeProgress = document.getElementById("gaugeProgress");
  gaugeProgress.style.strokeDashoffset = offset;
  gaugeProgress.style.stroke = catColor;

  // Ambient Glow
  const ambientGlow = document.getElementById("ambientGlow");
  ambientGlow.style.backgroundColor = catColor;

  // 3. Weather Stats
  const weather = data.weather || {};
  document.getElementById("weatherTemp").textContent = `${weather.temperature || 25} °C`;
  document.getElementById("weatherHumidity").textContent = `${weather.humidity || 55} %`;
  document.getElementById("weatherWind").textContent = `${weather.wind_speed || 3.0} m/s`;

  // 4. Pollutants
  const p = data.pollutants || {};
  document.getElementById("valPm25").textContent = (p.pm25 || 0).toFixed(1);
  document.getElementById("valPm10").textContent = (p.pm10 || 0).toFixed(1);
  document.getElementById("valNo2").textContent = (p.no2 || 0).toFixed(1);
  document.getElementById("valSo2").textContent = (p.so2 || 0).toFixed(1);
  document.getElementById("valCo").textContent = (p.co || 0).toFixed(2);
  document.getElementById("valO3").textContent = (p.o3 || 0).toFixed(1);

  // 5. AI Health & Fitness Advisor
  const act = document.getElementById("activityInput").value.trim() || "Planned Activity";
  document.getElementById("targetActivityLabel").textContent = act;
  document.getElementById("healthImpactBox").textContent = catInfo.health_impact || "";

  const maskBadge = document.getElementById("maskBadge");
  if (catInfo.mask_recommended) {
    maskBadge.className = "px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 flex items-center gap-1";
    maskBadge.innerHTML = `<i data-lucide="shield-alert" class="w-3.5 h-3.5"></i> N95 Mask Required`;
  } else {
    maskBadge.className = "px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 flex items-center gap-1";
    maskBadge.innerHTML = `<i data-lucide="shield-check" class="w-3.5 h-3.5"></i> Mask Optional`;
  }

  const adviceContainer = document.getElementById("adviceContainer");
  const adviceText = data.activity_advice || "";
  const lines = adviceText.split("\n").filter(l => l.trim().length > 0);
  adviceContainer.innerHTML = lines.map(line => `
    <div class="flex items-start gap-2.5 p-3 rounded-xl bg-purple-50/60 border border-purple-100/80">
      <span class="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0"></span>
      <p class="leading-relaxed">${line.replace(/^[•\-\*]\s*/, "")}</p>
    </div>
  `).join("");

  // 6. Synchronize What-If Simulator sliders with live readings
  document.getElementById("sliderPm25").value = Math.min(350, Math.round(p.pm25 || 75));
  document.getElementById("labelSliderPm25").textContent = `${Math.round(p.pm25 || 75)} µg/m³`;

  document.getElementById("sliderPm10").value = Math.min(500, Math.round(p.pm10 || 130));
  document.getElementById("labelSliderPm10").textContent = `${Math.round(p.pm10 || 130)} µg/m³`;

  document.getElementById("sliderNo2").value = Math.min(250, Math.round(p.no2 || 45));
  document.getElementById("labelSliderNo2").textContent = `${Math.round(p.no2 || 45)} µg/m³`;

  document.getElementById("sliderSo2").value = Math.min(200, Math.round(p.so2 || 20));
  document.getElementById("labelSliderSo2").textContent = `${Math.round(p.so2 || 20)} µg/m³`;

  document.getElementById("sliderWind").value = Math.min(15, (weather.wind_speed || 3.5).toFixed(1));
  document.getElementById("labelSliderWind").textContent = `${(weather.wind_speed || 3.5).toFixed(1)} m/s`;

  document.getElementById("sliderTemp").value = Math.round(weather.temperature || 26);
  document.getElementById("labelSliderTemp").textContent = `${Math.round(weather.temperature || 26)} °C`;

  // Trigger simulator prediction with current values
  triggerSimulatorPrediction();

  // 7. Update Charts
  renderTrendChart(data.hourly_trend || []);
  renderRadarChart(p);

  lucide.createIcons();
}

async function requestActivityAdvice() {
  if (!currentData) return;
  const act = document.getElementById("activityInput").value.trim() || "workout";
  
  try {
    const res = await fetch("/api/advice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        aqi: currentData.aqi,
        activity: act,
        pm25: currentData.pollutants?.pm25 || 50,
        pm10: currentData.pollutants?.pm10 || 100,
      }),
    });
    const result = await res.json();
    currentData.activity_advice = result.advice;
    
    document.getElementById("targetActivityLabel").textContent = act;
    const adviceContainer = document.getElementById("adviceContainer");
    const lines = result.advice.split("\n").filter(l => l.trim().length > 0);
    adviceContainer.innerHTML = lines.map(line => `
      <div class="flex items-start gap-2.5 p-3 rounded-xl bg-purple-50/60 border border-purple-100/80">
        <span class="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0"></span>
        <p class="leading-relaxed">${line.replace(/^[•\-\*]\s*/, "")}</p>
      </div>
    `).join("");
    lucide.createIcons();
  } catch (err) {
    console.error("Advice request error:", err);
  }
}

function onSimulatorInput() {
  // Update slider label text immediately
  document.getElementById("labelSliderPm25").textContent = `${document.getElementById("sliderPm25").value} µg/m³`;
  document.getElementById("labelSliderPm10").textContent = `${document.getElementById("sliderPm10").value} µg/m³`;
  document.getElementById("labelSliderNo2").textContent = `${document.getElementById("sliderNo2").value} µg/m³`;
  document.getElementById("labelSliderSo2").textContent = `${document.getElementById("sliderSo2").value} µg/m³`;
  document.getElementById("labelSliderWind").textContent = `${document.getElementById("sliderWind").value} m/s`;
  document.getElementById("labelSliderTemp").textContent = `${document.getElementById("sliderTemp").value} °C`;

  clearTimeout(simulatorTimer);
  simulatorTimer = setTimeout(triggerSimulatorPrediction, 150);
}

async function triggerSimulatorPrediction() {
  const payload = {
    pm25: parseFloat(document.getElementById("sliderPm25").value),
    pm10: parseFloat(document.getElementById("sliderPm10").value),
    no2: parseFloat(document.getElementById("sliderNo2").value),
    so2: parseFloat(document.getElementById("sliderSo2").value),
    co: currentData?.pollutants?.co || 1.0,
    o3: currentData?.pollutants?.o3 || 35.0,
    nh3: currentData?.pollutants?.nh3 || 15.0,
    wind_speed: parseFloat(document.getElementById("sliderWind").value),
    temperature: parseFloat(document.getElementById("sliderTemp").value),
    humidity: currentData?.weather?.humidity || 55.0,
    pressure: currentData?.weather?.pressure || 1012.0,
    rainfall: 0.0,
  };

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const pred = await res.json();

    document.getElementById("simPredictedAQI").textContent = pred.predicted_aqi;
    document.getElementById("simFormulaAQI").textContent = pred.calculated_cpcb_aqi;

    const catPill = document.getElementById("simCategoryPill");
    catPill.textContent = pred.predicted_category;
    catPill.style.backgroundColor = pred.category_info.color || "#f59e0b";

    // Update Probability Bar
    const probs = pred.category_probabilities || {};
    const probBarContainer = document.getElementById("probBarContainer");
    const probLabelsContainer = document.getElementById("probLabelsContainer");

    const colorMap = {
      "Good": "#10b981",
      "Satisfactory": "#84cc16",
      "Moderate": "#eab308",
      "Poor": "#f97316",
      "Very Poor": "#ef4444",
      "Severe": "#7f1d1d",
      "Hazardous": "#881337",
    };

    let barHtml = "";
    let labelsHtml = "";
    for (const [cls, val] of Object.entries(probs)) {
      if (val > 0) {
        const c = colorMap[cls] || "#64748b";
        barHtml += `<div style="width: ${val}%; background-color: ${c}" class="h-full transition-all duration-300" title="${cls}: ${val}%"></div>`;
        labelsHtml += `<span class="flex items-center gap-1 font-semibold"><span class="w-2 h-2 rounded-full" style="background-color: ${c}"></span> ${cls}: <strong>${val}%</strong></span>`;
      }
    }
    probBarContainer.innerHTML = barHtml;
    probLabelsContainer.innerHTML = labelsHtml;

    // If 24h forecast is present, update trend chart
    if (pred.forecast_24h && pred.forecast_24h.length > 0) {
      updateForecastChart(pred.forecast_24h);
    }
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

// ---------------- Chart.js Renderers ---------------- //

function renderTrendChart(hourlyData) {
  const ctx = document.getElementById("trendChart").getContext("2d");
  
  const labels = hourlyData.map(h => h.time);
  const values = hourlyData.map(h => h.pm25);

  if (trendChartInstance) {
    trendChartInstance.destroy();
  }

  const gradient = ctx.createLinearGradient(0, 0, 0, 200);
  gradient.addColorStop(0, "rgba(59, 130, 246, 0.4)");
  gradient.addColorStop(1, "rgba(59, 130, 246, 0.0)");

  trendChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "PM2.5 (µg/m³)",
        data: values,
        borderColor: "#2563eb",
        backgroundColor: gradient,
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 5,
        borderWidth: 2.5,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1e293b",
          titleFont: { weight: "bold" },
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 10 } }
        },
        y: {
          grid: { color: "#f1f5f9" },
          ticks: { font: { size: 10 } },
          beginAtZero: true,
        }
      }
    }
  });
}

function updateForecastChart(forecastList) {
  if (!trendChartInstance) return;
  trendChartInstance.data.labels = forecastList.map(f => f.hour);
  trendChartInstance.data.datasets[0].label = "Predicted 24h AQI";
  trendChartInstance.data.datasets[0].data = forecastList.map(f => f.predicted_aqi);
  trendChartInstance.data.datasets[0].borderColor = "#8b5cf6";
  trendChartInstance.update();
}

function renderRadarChart(pollutants) {
  const ctx = document.getElementById("radarChart").getContext("2d");

  // Relative benchmark values
  const labels = ["PM2.5", "PM10", "NO₂", "SO₂", "CO", "O₃"];
  const values = [
    Math.min(100, ((pollutants.pm25 || 20) / 120) * 100),
    Math.min(100, ((pollutants.pm10 || 40) / 200) * 100),
    Math.min(100, ((pollutants.no2 || 20) / 80) * 100),
    Math.min(100, ((pollutants.so2 || 10) / 80) * 100),
    Math.min(100, ((pollutants.co || 1) / 4) * 100),
    Math.min(100, ((pollutants.o3 || 25) / 100) * 100),
  ];

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [{
        label: "Toxicity % of Safe Limit",
        data: values,
        backgroundColor: "rgba(139, 92, 246, 0.2)",
        borderColor: "#8b5cf6",
        pointBackgroundColor: "#8b5cf6",
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        r: {
          angleLines: { color: "#e2e8f0" },
          grid: { color: "#e2e8f0" },
          suggestedMin: 0,
          suggestedMax: 100,
          ticks: { display: false }
        }
      }
    }
  });
}

async function loadHistoricalData() {
  try {
    const res = await fetch("/api/historical");
    const data = await res.json();
    const cities = data.cities || [];

    const ctx = document.getElementById("cityChart").getContext("2d");
    if (cityChartInstance) cityChartInstance.destroy();

    const labels = cities.map(c => c.city);
    const meanAqi = cities.map(c => c.aqi_mean);
    const maxAqi = cities.map(c => c.aqi_max);

    cityChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Mean AQI",
            data: meanAqi,
            backgroundColor: "#3b82f6",
            borderRadius: 6,
          },
          {
            label: "Max Winter Peak",
            data: maxAqi,
            backgroundColor: "#f43f5e",
            borderRadius: 6,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } },
        },
        scales: {
          x: { grid: { display: false } },
          y: { beginAtZero: true, grid: { color: "#f1f5f9" } }
        }
      }
    });
  } catch (err) {
    console.error("Historical error:", err);
  }
}

async function loadModelMetrics() {
  try {
    const res = await fetch("/api/metrics");
    const metrics = await res.json();

    if (metrics.regression) {
      document.getElementById("metricR2").textContent = metrics.regression.r2_score;
      document.getElementById("metricMAE").textContent = metrics.regression.mae;
    }
    if (metrics.classification) {
      document.getElementById("metricAcc").textContent = `${(metrics.classification.accuracy * 100).toFixed(1)}%`;
    }

    const importances = metrics.feature_importances || {};
    const topFeatures = Object.entries(importances).slice(0, 6);

    const ctx = document.getElementById("importanceChart").getContext("2d");
    if (importanceChartInstance) importanceChartInstance.destroy();

    importanceChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: topFeatures.map(f => f[0]),
        datasets: [{
          data: topFeatures.map(f => (f[1] * 100).toFixed(1)),
          backgroundColor: "#8b5cf6",
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (item) => `Importance: ${item.raw}%`
            }
          }
        },
        scales: {
          x: { beginAtZero: true, grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });
  } catch (err) {
    console.error("Metrics load error:", err);
  }
}

function exportReport() {
  if (!currentData) return;
  const report = {
    generated_at: new Date().toISOString(),
    station: currentData.city,
    country: currentData.country,
    aqi: currentData.aqi,
    standard: currentStandard,
    dominant_pollutant: currentData.dominant_pollutant,
    category: currentData.category,
    pollutants: currentData.pollutants,
    sub_indices: currentData.sub_indices,
    weather: currentData.weather,
    activity_recommendations: currentData.activity_advice,
  };

  const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `AeroGuard_AQI_Report_${currentData.city}_${new Date().toISOString().split("T")[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

