/**
 * PlantCare AI - Frontend Client Orchestration
 * Handles leaf image preprocessing, API calls, spatial query rendering,
 * and atomic stock reservation workflows.
 */

// ---------------------------------------------------------------------------
// 1. Curated Benchmark High-Resolution Botanical Samples
// ---------------------------------------------------------------------------

let benchmarkCache = {};

// Fallback high-res canvas generator if offline or pre-fetch
function createSyntheticLeafSample(patternType) {
    if (benchmarkCache[patternType]) {
        return benchmarkCache[patternType];
    }

    const canvas = document.createElement("canvas");
    canvas.width = 448;
    canvas.height = 448;
    const ctx = canvas.getContext("2d");

    // Botanical Dark Field Background
    ctx.fillStyle = "#0b1118";
    ctx.fillRect(0, 0, 448, 448);

    // Leaf outline & organic curvature
    ctx.save();
    ctx.beginPath();
    const cx = 224, cy = 224;

    if (patternType === "healthy_corn") {
        // Slender monocot corn leaf blade
        ctx.fillStyle = "#2e7d32";
        ctx.beginPath();
        for (let i = 0; i <= 360; i++) {
            const rad = i * Math.PI / 180;
            const r = 190 * (1 - 0.85 * Math.pow(Math.sin(rad / 2), 2));
            const px = cx + (r * 0.42) * Math.sin(rad);
            const py = cy - r * Math.cos(rad);
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.fill();

        // Parallel venation
        ctx.strokeStyle = "#4caf50";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(cx, 40);
        ctx.lineTo(cx, 410);
        ctx.stroke();

        ctx.lineWidth = 1.5;
        for (let off = -24; off <= 24; off += 12) {
            if (off === 0) continue;
            ctx.beginPath();
            ctx.moveTo(cx + off, 60);
            ctx.lineTo(cx + off, 390);
            ctx.stroke();
        }
    } else if (patternType === "rice_blast") {
        // Rice leaf blade with spindle lesions
        ctx.fillStyle = "#2e7d32";
        ctx.beginPath();
        for (let i = 0; i <= 360; i++) {
            const rad = i * Math.PI / 180;
            const r = 195 * (1 - 0.88 * Math.pow(Math.sin(rad / 2), 2));
            const px = cx + (r * 0.38) * Math.sin(rad);
            const py = cy - r * Math.cos(rad);
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.fill();

        // Rice midrib
        ctx.strokeStyle = "#4caf50";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(cx, 45);
        ctx.lineTo(cx, 405);
        ctx.stroke();

        // Spindle diamond-shaped blast lesions (olive-brown calibrated necrosis)
        const blastSpots = [
            { x: cx, y: 150, rx: 14, ry: 32 },
            { x: cx + 2, y: 240, rx: 16, ry: 36 },
            { x: cx - 2, y: 320, rx: 12, ry: 28 }
        ];
        blastSpots.forEach(s => {
            ctx.fillStyle = "#32280f";
            ctx.beginPath();
            ctx.ellipse(s.x, s.y, s.rx, s.ry, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = "#5f5819";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Gray necrotic center
            ctx.fillStyle = "#46411e";
            ctx.beginPath();
            ctx.ellipse(s.x, s.y, s.rx * 0.5, s.ry * 0.5, 0, 0, Math.PI * 2);
            ctx.fill();
        });
    } else if (patternType === "potato_late_blight") {
        // Broad potato leaflet
        ctx.fillStyle = "#267a2e";
        ctx.beginPath();
        for (let i = 0; i <= 360; i++) {
            const rad = i * Math.PI / 180;
            const r = 180 * (1 - 0.5 * Math.pow(Math.sin(rad / 2), 2));
            const px = cx + (r * 0.88) * Math.sin(rad);
            const py = cy - r * Math.cos(rad);
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.fill();

        // Spreading water-soaked necrotic lesions from margin
        ctx.fillStyle = "#32280f";
        ctx.beginPath();
        ctx.ellipse(cx, 160, 110, 80, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.ellipse(cx - 30, 270, 75, 70, 0, 0, Math.PI * 2);
        ctx.fill();

        // Downy fungal halo
        ctx.strokeStyle = "#6e733c";
        ctx.lineWidth = 3;
        ctx.stroke();
    } else {
        // Tomato Early Blight (Default) - Pinnate serrated leaf with concentric lesions
        ctx.fillStyle = "#287e30";
        ctx.beginPath();
        for (let i = 0; i <= 360; i++) {
            const rad = i * Math.PI / 180;
            const r = 175 * (1 - 0.65 * Math.pow(Math.sin(rad / 2), 2)) + 8 * Math.sin(rad * 12) * (1 - Math.abs(Math.cos(rad)));
            const px = cx + (r * 0.8) * Math.sin(rad);
            const py = cy - r * Math.cos(rad);
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.fill();

        // Foliar veins
        ctx.strokeStyle = "#449e4c";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(cx, 70);
        ctx.lineTo(cx, 390);
        ctx.stroke();

        ctx.lineWidth = 2;
        for (let y = 130; y < 360; y += 38) {
            ctx.beginPath();
            ctx.moveTo(cx, y);
            ctx.lineTo(cx - 65, y - 30);
            ctx.moveTo(cx, y);
            ctx.lineTo(cx + 65, y - 30);
            ctx.stroke();
        }

        // Concentric target-board brown lesions with chlorotic yellow halo
        const spots = [
            { x: 180, y: 175, r: 36 },
            { x: 260, y: 230, r: 42 },
            { x: 200, y: 300, r: 28 }
        ];
        spots.forEach(s => {
            // Chlorotic yellow-green halo
            ctx.fillStyle = "#5f5819";
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r + 6, 0, Math.PI * 2);
            ctx.fill();

            // Concentric necrotic rings
            ctx.fillStyle = "#32280f";
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = "#3e3212";
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 0.65, 0, Math.PI * 2);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 0.35, 0, Math.PI * 2);
            ctx.stroke();
        });
    }
    ctx.restore();

    return canvas.toDataURL("image/jpeg", 0.92);
}

// Pre-load pre-rendered high-res benchmark samples
async function loadBenchmarkSamples() {
    try {
        const resp = await fetch("/static/samples_b64.json");
        if (resp.ok) {
            benchmarkCache = await resp.json();
            // Refresh preview if currently on default
            const preview = document.getElementById("imagePreview");
            if (preview && benchmarkCache["tomato_early_blight"]) {
                state.currentImageBase64 = benchmarkCache["tomato_early_blight"];
                preview.src = state.currentImageBase64;
            }
        }
    } catch (e) {
        console.warn("Using canvas procedural leaf samples fallback:", e);
    }
}

// ---------------------------------------------------------------------------
// 2. Application State
// ---------------------------------------------------------------------------

const state = {
    selectedCrop: "Tomato",
    currentImageBase64: createSyntheticLeafSample("tomato_early_blight"),
    lastDiagnosis: null,
    lastReservation: null,
    searchRadius: 25.0,
    userLocation: { lat: 28.6139, lon: 77.2090 },
    storesDirectory: {},
    mapInstance: null,
    mapMarkersLayer: null,
    mapRadiusCircle: null,
    farmerMarker: null,
};

// ---------------------------------------------------------------------------
// 3. DOM Elements & Initialization
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initSampleSelector();
    initUploadDropzone();
    initDiagnosisRunner();
    initSpatialSearch();
    initReservationForm();
    initPosPortal();
    fetchSystemTelemetry();
    loadBenchmarkSamples();
    initPrescriptionPdfGenerator();
    initPickupPdfGenerator();

    // Initial leaf preview
    const preview = document.getElementById("imagePreview");
    if (preview) {
        preview.src = state.currentImageBase64;
    }
});

// ---------------------------------------------------------------------------
// 4. Navigation & Tabs
// ---------------------------------------------------------------------------

function initTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");

            tabButtons.forEach(b => b.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add("active");
            }

            // Invalidate Leaflet map size when switching to tab-stores
            if (targetId === "tab-stores" && state.mapInstance) {
                setTimeout(() => {
                    state.mapInstance.invalidateSize();
                }, 100);
            }
        });
    });
}

// ---------------------------------------------------------------------------
// 5. Sample & Upload Handlers
// ---------------------------------------------------------------------------

function initSampleSelector() {
    const cropSelect = document.getElementById("cropSelect");
    const sampleButtons = document.querySelectorAll(".sample-btn");
    const preview = document.getElementById("imagePreview");
    const previewInfo = document.getElementById("previewInfo");

    cropSelect.addEventListener("change", (e) => {
        state.selectedCrop = e.target.value;
    });

    sampleButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            sampleButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const sampleKey = btn.getAttribute("data-sample");
            let crop = "Tomato";
            if (sampleKey === "potato_late_blight") crop = "Potato";
            if (sampleKey === "healthy_corn") crop = "Corn";
            if (sampleKey === "rice_blast") crop = "Rice";

            cropSelect.value = crop;
            state.selectedCrop = crop;

            const base64Data = benchmarkCache[sampleKey] || createSyntheticLeafSample(sampleKey);
            state.currentImageBase64 = base64Data;
            preview.src = base64Data;
            previewInfo.textContent = `Curated Benchmark: ${btn.textContent}`;
        });
    });
}

function initUploadDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const preview = document.getElementById("imagePreview");
    const previewInfo = document.getElementById("previewInfo");

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("hover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("hover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("hover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
        }
    });

    function handleFileUpload(file) {
        if (!file.type.startsWith("image/")) {
            alert("Please select a valid image file (.jpg, .png, .webp).");
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            const b64 = event.target.result;
            state.currentImageBase64 = b64;
            preview.src = b64;
            previewInfo.textContent = `Uploaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

            // Unset sample button highlights
            document.querySelectorAll(".sample-btn").forEach(b => b.classList.remove("active"));
        };
        reader.readAsDataURL(file);
    }
}

// ---------------------------------------------------------------------------
// 6. Pathology Diagnosis & Animated Result Execution
// ---------------------------------------------------------------------------

function initDiagnosisRunner() {
    const btn = document.getElementById("btnRunDiagnosis");
    const btnFindStores = document.getElementById("btnFindStoresForPrescription");
    const previewBox = document.getElementById("previewContainer");

    btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.textContent = "⏳ Executing Computer Vision Pathology Inference...";
        
        // Start scanning laser animation on leaf preview
        if (previewBox) {
            previewBox.classList.add("scanning");
        }

        try {
            const response = await fetch("/api/v1/diagnose", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    crop_type: state.selectedCrop,
                    image_base64: state.currentImageBase64,
                }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Diagnosis failed");
            }

            const data = await response.json();
            state.lastDiagnosis = data;
            
            // Render results with step-by-step focus animation
            renderDiagnosisResultsWithAnimation(data);
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            if (previewBox) {
                previewBox.classList.remove("scanning");
            }
            btn.disabled = false;
            btn.textContent = "🔍 Execute Computer Vision Pathology Inference";
        }
    });

    btnFindStores.addEventListener("click", () => {
        if (!state.lastDiagnosis) return;

        // Switch to Store Routing tab
        const storeTabBtn = document.querySelector(".tab-btn[data-tab='tab-stores']");
        if (storeTabBtn) storeTabBtn.click();

        // Pre-select medicine from prescription
        const selectMed = document.getElementById("selectMedicine");
        if (state.lastDiagnosis.chemical_treatments.length > 0) {
            selectMed.value = state.lastDiagnosis.chemical_treatments[0].id;
        } else if (state.lastDiagnosis.organic_treatments.length > 0) {
            selectMed.value = state.lastDiagnosis.organic_treatments[0].id;
        }

        // Trigger spatial search
        document.getElementById("btnSearchStores").click();
    });
}

function renderDiagnosisResultsWithAnimation(data) {
    const placeholder = document.getElementById("diagPlaceholder");
    const resBox = document.getElementById("diagResults");

    const diagHeader = resBox.querySelector(".diag-header-summary");
    const meterCard = resBox.querySelector(".severity-meter-card");
    const actionsCard = resBox.querySelector(".actions-box");
    const treatGrid = resBox.querySelector(".treatment-grid");
    const storeNavBtn = resBox.querySelector("#btnFindStoresForPrescription");
    const severityBar = document.getElementById("resSeverityBar");

    // 1. Immediately hide all result sub-sections BEFORE revealing resBox so there is ZERO flashing
    [diagHeader, meterCard, actionsCard, treatGrid, storeNavBtn].forEach(el => {
        if (el) {
            el.classList.remove("diag-section-reveal");
            el.classList.add("diag-section-hidden");
        }
    });

    if (severityBar) {
        severityBar.style.transition = "none";
        severityBar.style.width = "0%";
    }

    // 2. Hide placeholder and reveal result container (its children are hidden via diag-section-hidden)
    placeholder.classList.add("hidden");
    resBox.classList.remove("hidden");

    // 3. Populate data into hidden elements
    document.getElementById("resCrop").textContent = data.crop;
    document.getElementById("resDisease").textContent = data.disease_name;
    document.getElementById("resScientific").textContent = data.scientific_name;
    document.getElementById("resConfidence").querySelector(".conf-num").textContent =
        `${(data.confidence_score * 100).toFixed(1)}%`;

    document.getElementById("resSeverity").textContent =
        `${data.severity} (${data.affected_percentage}% affected)`;

    // Render Immediate Actions
    const actionsList = document.getElementById("resActions");
    actionsList.innerHTML = "";
    data.immediate_actions.forEach(action => {
        const li = document.createElement("li");
        li.textContent = action;
        actionsList.appendChild(li);
    });

    // Render Chemical Treatments
    const chemList = document.getElementById("chemicalTreatmentsList");
    chemList.innerHTML = "";
    if (data.chemical_treatments.length === 0) {
        chemList.innerHTML = `<div class="treatment-item text-muted">No synthetic chemicals recommended (Healthy / Organic Preventive protocol).</div>`;
    } else {
        data.chemical_treatments.forEach(t => {
            const item = document.createElement("div");
            item.className = "treatment-item";
            item.innerHTML = `
                <div class="med-name">${t.name}</div>
                <div class="med-detail"><strong>Active Ingredient:</strong> ${t.active_ingredient}</div>
                <div class="med-detail"><strong>Dosage/Acre:</strong> ${t.dosage_per_acre}</div>
                <div class="med-detail"><strong>Dilution:</strong> ${t.dilution_instructions || "Standard foliar spray"}</div>
                <span class="med-phi">PHI: ${t.pre_harvest_interval_days} Days Safety Period</span>
            `;
            chemList.appendChild(item);
        });
    }

    // Render Organic Treatments
    const orgList = document.getElementById("organicTreatmentsList");
    orgList.innerHTML = "";
    data.organic_treatments.forEach(t => {
        const item = document.createElement("div");
        item.className = "treatment-item";
        item.innerHTML = `
            <div class="med-name">${t.name}</div>
            <div class="med-detail"><strong>Active Agent:</strong> ${t.active_ingredient}</div>
            <div class="med-detail"><strong>Dosage/Acre:</strong> ${t.dosage_per_acre}</div>
            <div class="med-detail"><strong>Dilution:</strong> ${t.dilution_instructions || "Chlorine-free water spray"}</div>
            <span class="med-phi green">Certified Organic • 0-Day Waiting Period</span>
        `;
        orgList.appendChild(item);
    });

    // 4. Staggered reveal one-by-one directly without any flash

    // Step 1: Reveal Pathology Header (Crop, Disease Name, Confidence)
    setTimeout(() => {
        if (diagHeader) {
            diagHeader.classList.remove("diag-section-hidden");
            diagHeader.classList.add("diag-section-reveal");
        }
    }, 50);

    // Step 2: Reveal Severity Meter & animate progress bar smoothly
    setTimeout(() => {
        if (meterCard) {
            meterCard.classList.remove("diag-section-hidden");
            meterCard.classList.add("diag-section-reveal");
        }
        if (severityBar) {
            severityBar.style.transition = "width 1.1s cubic-bezier(0.16, 1, 0.3, 1)";
            const targetWidth = Math.min(100, Math.max(5, data.affected_percentage));
            severityBar.style.width = `${targetWidth}%`;
        }
    }, 450);

    // Step 3: Reveal Immediate Containment Actions
    setTimeout(() => {
        if (actionsCard) {
            actionsCard.classList.remove("diag-section-hidden");
            actionsCard.classList.add("diag-section-reveal");
        }
    }, 850);

    // Step 4: Reveal Dual Treatment Regimens & Store Locator Button
    setTimeout(() => {
        if (treatGrid) {
            treatGrid.classList.remove("diag-section-hidden");
            treatGrid.classList.add("diag-section-reveal");
        }
        if (storeNavBtn) {
            storeNavBtn.classList.remove("diag-section-hidden");
            storeNavBtn.classList.add("diag-section-reveal");
        }
    }, 1250);
}

// ---------------------------------------------------------------------------
// 7. Hyperlocal Spatial Inventory Routing & Interactive Leaflet Map
// ---------------------------------------------------------------------------

function initSpatialSearch() {
    const btnSearch = document.getElementById("btnSearchStores");
    const radiusSlider = document.getElementById("inputRadius");
    const radiusLabel = document.getElementById("radiusLabel");
    const btnGps = document.getElementById("btnUseGps");
    const presets = document.querySelectorAll(".coord-preset");

    // Initialize Leaflet Map
    initLeafletMap();

    radiusSlider.addEventListener("input", (e) => {
        radiusLabel.textContent = `${e.target.value} km`;
        state.searchRadius = parseFloat(e.target.value);
        updateMapFarmerRadius();
    });

    presets.forEach(p => {
        p.addEventListener("click", () => {
            const lat = parseFloat(p.getAttribute("data-lat"));
            const lon = parseFloat(p.getAttribute("data-lon"));
            document.getElementById("inputLat").value = lat;
            document.getElementById("inputLon").value = lon;
            updateMapFarmerLocation(lat, lon);
        });
    });

    btnGps.addEventListener("click", () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            pos => {
                const lat = parseFloat(pos.coords.latitude.toFixed(4));
                const lon = parseFloat(pos.coords.longitude.toFixed(4));
                document.getElementById("inputLat").value = lat;
                document.getElementById("inputLon").value = lon;
                updateMapFarmerLocation(lat, lon);
            },
            err => alert(`Unable to acquire GPS coordinates: ${err.message}`)
        );
    });

    btnSearch.addEventListener("click", async () => {
        btnSearch.disabled = true;
        btnSearch.textContent = "⚡ Searching Nearby Verified Retailers...";

        const lat = parseFloat(document.getElementById("inputLat").value);
        const lon = parseFloat(document.getElementById("inputLon").value);
        const radius = parseFloat(radiusSlider.value);
        const medId = document.getElementById("selectMedicine").value;
        const inStockOnly = document.getElementById("checkInStockOnly").checked;

        updateMapFarmerLocation(lat, lon);

        try {
            const response = await fetch("/api/v1/medicines/nearby", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    latitude: lat,
                    longitude: lon,
                    medicine_ids: [medId],
                    radius_km: radius,
                    in_stock_only: inStockOnly,
                }),
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Spatial query failed");
            }

            const results = await response.json();
            renderStoreResults(results);
            updateMapStoreMarkers(results, lat, lon);
        } catch (error) {
            alert(`Spatial Error: ${error.message}`);
        } finally {
            btnSearch.disabled = false;
            btnSearch.textContent = "⚡ Execute Hyperlocal Geospatial Inventory Query";
        }
    });

    // Initial pre-load of store locations for map
    fetchStoreDirectory();
}

async function fetchStoreDirectory() {
    try {
        const response = await fetch("/api/v1/stores");
        if (response.ok) {
            const stores = await response.json();
            stores.forEach(s => {
                state.storesDirectory[s.store_id] = s;
            });
        }
    } catch (e) {
        console.warn("Could not pre-fetch stores directory:", e);
    }
}

function initLeafletMap() {
    const mapEl = document.getElementById("leafletMap");
    if (!mapEl || typeof L === "undefined") return;

    const initialLat = 28.6139;
    const initialLon = 77.2090;

    // Create Leaflet map instance
    state.mapInstance = L.map("leafletMap", {
        center: [initialLat, initialLon],
        zoom: 11,
        zoomControl: true,
    });

    // Free OpenStreetMap tile layer
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(state.mapInstance);

    // Layer group for store pins
    state.mapMarkersLayer = L.layerGroup().addTo(state.mapInstance);

    // Set initial farmer pin & search radius circle
    updateMapFarmerLocation(initialLat, initialLon);
}

function updateMapFarmerLocation(lat, lon) {
    if (!state.mapInstance || typeof L === "undefined") return;

    state.userLocation = { lat, lon };

    // Update or create farmer marker
    if (state.farmerMarker) {
        state.farmerMarker.setLatLng([lat, lon]);
    } else {
        const farmerIcon = L.divIcon({
            className: "custom-farmer-pin",
            html: `<div style="background:#0284c7; width:22px; height:22px; border-radius:50%; border:3px solid #ffffff; box-shadow:0 0 12px #38bdf8; display:flex; align-items:center; justify-content:center; color:#fff; font-size:11px;">📍</div>`,
            iconSize: [22, 22],
            iconAnchor: [11, 11],
        });
        state.farmerMarker = L.marker([lat, lon], { icon: farmerIcon, zIndexOffset: 1000 })
            .addTo(state.mapInstance)
            .bindPopup(`<strong style="color:#38bdf8;">Farmer Location</strong><br><span style="font-size:0.75rem; color:#94a3b8;">${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E</span>`);
    }

    updateMapFarmerRadius();
    state.mapInstance.panTo([lat, lon]);
}

function updateMapFarmerRadius() {
    if (!state.mapInstance || typeof L === "undefined") return;

    const lat = state.userLocation.lat;
    const lon = state.userLocation.lon;
    const radiusMeters = state.searchRadius * 1000;

    if (state.mapRadiusCircle) {
        state.mapRadiusCircle.setLatLng([lat, lon]);
        state.mapRadiusCircle.setRadius(radiusMeters);
    } else {
        state.mapRadiusCircle = L.circle([lat, lon], {
            radius: radiusMeters,
            color: "#10b981",
            fillColor: "#10b981",
            fillOpacity: 0.08,
            weight: 2,
            dashArray: "6, 6",
        }).addTo(state.mapInstance);
    }
}

function updateMapStoreMarkers(stores, farmerLat, farmerLon) {
    if (!state.mapInstance || !state.mapMarkersLayer || typeof L === "undefined") return;

    state.mapMarkersLayer.clearLayers();
    const badge = document.getElementById("mapStatusBadge");
    if (badge) {
        badge.textContent = `${stores.length} Retailers Displayed`;
    }

    const boundsGroup = [];
    boundsGroup.push([farmerLat, farmerLon]);

    stores.forEach(s => {
        // Resolve store coordinates from directory or catalog fallback
        const dirStore = state.storesDirectory[s.store_id];
        let storeLat = dirStore ? dirStore.latitude : null;
        let storeLon = dirStore ? dirStore.longitude : null;

        // Fallback approximation if catalog not yet loaded
        if (storeLat == null) {
            // Store coordinates mapped from known constants
            const knownCoords = {
                "STR-001": [28.6139, 77.2090],
                "STR-002": [28.6420, 77.1850],
                "STR-003": [28.5800, 77.2400],
                "STR-004": [28.7041, 77.1025],
                "STR-005": [28.5700, 77.3200],
                "STR-006": [28.4595, 77.0266],
                "STR-007": [28.6692, 77.4538],
                "STR-008": [28.9845, 77.7064],
            };
            if (knownCoords[s.store_id]) {
                storeLat = knownCoords[s.store_id][0];
                storeLon = knownCoords[s.store_id][1];
            }
        }

        if (storeLat != null && storeLon != null) {
            boundsGroup.push([storeLat, storeLon]);

            // Pin color based on stock status
            let pinColor = "#10b981"; // green (in stock > 10)
            let pinLabel = "✓";
            if (s.stock_quantity <= 0) {
                pinColor = "#ef4444"; // red (out of stock)
                pinLabel = "✕";
            } else if (s.stock_quantity <= 10) {
                pinColor = "#f97316"; // orange (low stock)
                pinLabel = "!";
            }

            const storeIcon = L.divIcon({
                className: "custom-store-pin",
                html: `<div style="background:${pinColor}; width:24px; height:24px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 10px ${pinColor}; display:flex; align-items:center; justify-content:center; color:#ffffff; font-weight:800; font-size:12px;">${pinLabel}</div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12],
            });

            const googleMapsNavUrl = `https://www.google.com/maps/dir/?api=1&origin=${farmerLat},${farmerLon}&destination=${storeLat},${storeLon}`;

            const popupContent = `
                <div class="map-popup-title">${s.store_name}</div>
                <div class="map-popup-meta">
                    <div>📍 ${s.store_address}</div>
                    <div>📞 ${s.store_phone}</div>
                    <div style="margin-top:4px;"><strong>${s.medicine_name}</strong></div>
                    <div style="color:${pinColor}; font-weight:700;">Stock: ${s.stock_quantity} (${s.unit_type}) • ₹${s.price_inr.toFixed(2)}</div>
                    <div>Distance: ${s.distance_km.toFixed(1)} km (~${s.estimated_driving_time_minutes} min)</div>
                </div>
                <div class="map-popup-action">
                    <button class="btn btn-xs btn-accent flex-1" onclick="selectStoreForHold('${s.store_id}', '${s.medicine_id}')">
                        Reserve Hold
                    </button>
                    <a href="${googleMapsNavUrl}" target="_blank" class="btn btn-xs btn-outline" style="text-decoration:none; display:inline-flex; align-items:center;">
                        🗺️ Navigate
                    </a>
                </div>
            `;

            L.marker([storeLat, storeLon], { icon: storeIcon })
                .addTo(state.mapMarkersLayer)
                .bindPopup(popupContent);
        }
    });

    if (boundsGroup.length > 1) {
        state.mapInstance.fitBounds(boundsGroup, { padding: [40, 40] });
    }
}

// Global hook for popup reserve action
window.selectStoreForHold = function(storeId, medId) {
    document.querySelector(".tab-btn[data-tab='tab-reserve']").click();
    const storeSelect = document.getElementById("resSelectStore");
    const medSelect = document.getElementById("resSelectMed");
    if (storeSelect) storeSelect.value = storeId;
    if (medSelect) medSelect.value = medId;
    updateReservationPriceSummary();
};

function renderStoreResults(stores) {
    const tbody = document.getElementById("storesTableBody");
    const subtitle = document.getElementById("storeCountSubtitle");
    tbody.innerHTML = "";

    subtitle.textContent = `Found ${stores.length} verified in-stock dealer(s) within selected radius`;

    if (stores.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted" style="padding: 24px;">
                    No verified stores with active stock found within this radius. Try increasing search radius (e.g. 50 km).
                </td>
            </tr>
        `;
        return;
    }

    stores.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <div style="font-weight:700; color:var(--text-primary);">${s.store_name}</div>
                <div class="text-muted" style="font-size:0.75rem; margin-top:2px;">📍 ${s.store_address} • 📞 ${s.store_phone}</div>
            </td>
            <td><strong style="color:var(--secondary);">${s.distance_km.toFixed(1)} km</strong></td>
            <td><span style="color:var(--text-secondary);">~${s.estimated_driving_time_minutes} min</span></td>
            <td>
                <span class="crop-tag">${s.medicine_id}</span>
                <div style="font-size:0.8rem; margin-top:3px; color:var(--text-secondary);">${s.medicine_name}</div>
            </td>
            <td>
                <span class="badge ${s.stock_quantity > 10 ? 'badge-green' : 'badge-orange'}">
                    ✓ ${s.stock_quantity} Available (${s.unit_type})
                </span>
            </td>
            <td><strong style="color:var(--text-primary); font-size:0.95rem;">₹${s.price_inr.toFixed(2)}</strong></td>
            <td>
                <button class="btn btn-xs btn-accent btn-quick-reserve"
                        data-store-id="${s.store_id}"
                        data-med-id="${s.medicine_id}"
                        data-price="${s.price_inr}">
                    Reserve Hold
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Attach quick reserve buttons
    document.querySelectorAll(".btn-quick-reserve").forEach(btn => {
        btn.addEventListener("click", () => {
            const storeId = btn.getAttribute("data-store-id");
            const medId = btn.getAttribute("data-med-id");

            // Switch to reservation tab
            document.querySelector(".tab-btn[data-tab='tab-reserve']").click();

            const storeSelect = document.getElementById("resSelectStore");
            const medSelect = document.getElementById("resSelectMed");

            if (storeSelect) storeSelect.value = storeId;
            if (medSelect) medSelect.value = medId;

            updateReservationPriceSummary();
        });
    });
}

// ---------------------------------------------------------------------------
// 8. 4-Hour Stock Reservation & Token Generation
// ---------------------------------------------------------------------------

function initReservationForm() {
    const form = document.getElementById("reservationForm");
    const qtyInput = document.getElementById("resQuantity");
    const medSelect = document.getElementById("resSelectMed");

    qtyInput.addEventListener("input", updateReservationPriceSummary);
    medSelect.addEventListener("change", updateReservationPriceSummary);

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector("button[type='submit']");
        submitBtn.disabled = true;
        submitBtn.textContent = "🔒 Securing Atomic 4-Hour Hold...";

        const payload = {
            farmer_name: document.getElementById("resFarmerName").value.trim(),
            farmer_phone: document.getElementById("resFarmerPhone").value.trim(),
            store_id: document.getElementById("resSelectStore").value,
            medicine_id: document.getElementById("resSelectMed").value,
            quantity_requested: parseInt(document.getElementById("resQuantity").value, 10),
            reservation_hours: 4,
        };

        try {
            const response = await fetch("/api/v1/medicines/reserve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Reservation failed");
            }

            const data = await response.json();
            renderReservationTicket(data);
        } catch (error) {
            alert(`Reservation Error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "🔒 Confirm & Lock 4-Hour Stock Reservation";
        }
    });
}

function updateReservationPriceSummary() {
    const qty = parseInt(document.getElementById("resQuantity").value, 10) || 1;
    const medSelect = document.getElementById("resSelectMed");
    const selectedText = medSelect.options[medSelect.selectedIndex].text;

    let pricePerUnit = 320.0;
    const match = selectedText.match(/₹([\d.]+)/);
    if (match) {
        pricePerUnit = parseFloat(match[1]);
    }

    const total = qty * pricePerUnit;
    document.getElementById("resEstimatedPrice").textContent = `₹${total.toFixed(2)}`;
}

function renderReservationTicket(data) {
    state.lastReservation = data;
    document.getElementById("tokenPlaceholder").classList.add("hidden");
    const tokenResult = document.getElementById("tokenResult");
    tokenResult.classList.remove("hidden");

    document.getElementById("dispPickupCode").textContent = data.pickup_code;
    document.getElementById("dispResId").textContent = data.reservation_id;
    document.getElementById("dispStatus").textContent = data.status;
    document.getElementById("dispStoreName").textContent = data.store_name;
    document.getElementById("dispMedName").textContent = data.medicine_name;
    document.getElementById("dispQty").textContent = `${data.quantity_reserved} Units`;
    document.getElementById("dispPrice").textContent = `₹${data.total_price_inr.toFixed(2)}`;
    document.getElementById("dispExpiry").textContent = data.expires_at;
}

// ---------------------------------------------------------------------------
// 9. Agro-Dealer POS Counter & Stock Ledgers
// ---------------------------------------------------------------------------

function initPosPortal() {
    const btnFulfill = document.getElementById("btnFulfillPickup");
    const inputCode = document.getElementById("posPickupCodeInput");
    const alertBox = document.getElementById("posAlert");
    const btnRefresh = document.getElementById("btnRefreshStores");

    btnFulfill.addEventListener("click", async () => {
        const code = inputCode.value.trim().toUpperCase();
        if (!code) {
            alert("Please enter a valid pickup code (e.g. PK-XXXXXX).");
            return;
        }

        try {
            const response = await fetch(`/api/v1/reservations/fulfill/${encodeURIComponent(code)}`, {
                method: "POST",
            });

            alertBox.classList.remove("hidden", "alert-success", "alert-error");

            if (!response.ok) {
                const err = await response.json();
                alertBox.classList.add("alert-error");
                alertBox.textContent = `❌ Verification Failed: ${err.detail}`;
            } else {
                const res = await response.json();
                alertBox.classList.add("alert-success");
                alertBox.textContent = `✓ Verified & Dispensed: ${res.message} [Customer: ${res.reservation.farmer_name}, Units: ${res.reservation.quantity_reserved}]`;
                inputCode.value = "";
                loadStoresCatalog();
            }
        } catch (error) {
            alertBox.classList.remove("hidden");
            alertBox.classList.add("alert-error");
            alertBox.textContent = `Connection Error: ${error.message}`;
        }
    });

    btnRefresh.addEventListener("click", loadStoresCatalog);
    loadStoresCatalog();
}

async function loadStoresCatalog() {
    const container = document.getElementById("storesCatalogGrid");
    if (!container) return;

    try {
        const response = await fetch("/api/v1/stores");
        if (!response.ok) return;

        const stores = await response.json();
        container.innerHTML = "";

        stores.forEach(s => {
            const card = document.createElement("div");
            card.className = "store-card-item";
            card.innerHTML = `
                <div class="store-card-name">${s.store_name}</div>
                <div class="store-card-license">Lic: ${s.government_license_number}</div>
                <div class="store-card-phone">📞 ${s.contact_phone}</div>
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:4px;">${s.physical_address}</div>
                <div style="font-size:0.72rem; color:var(--primary); margin-top:6px; font-weight:600;">🕒 ${s.operating_hours}</div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load stores catalog:", err);
    }
}

// ---------------------------------------------------------------------------
// 10. System Telemetry & Health Monitoring
// ---------------------------------------------------------------------------

async function fetchSystemTelemetry() {
    try {
        const response = await fetch("/api/v1/health");
        if (!response.ok) return;
        const data = await response.json();

        const elemStores = document.getElementById("telemetryStores");
        const elemMeds = document.getElementById("telemetryMeds");

        if (elemStores) elemStores.textContent = data.registered_stores;
        if (elemMeds) elemMeds.textContent = data.catalog_medicines;
    } catch (err) {
        console.warn("Telemetry fetch deferred:", err);
    }
}

// ---------------------------------------------------------------------------
// 11. Official Prescription & Pickup Slip PDF Generators
// ---------------------------------------------------------------------------

function initPrescriptionPdfGenerator() {
    const btn = document.getElementById("btnDownloadPrescriptionPdf");
    if (!btn) return;

    btn.addEventListener("click", () => {
        if (!state.lastDiagnosis) {
            alert("Please execute a foliar leaf diagnosis first before downloading the receipt.");
            return;
        }

        const { jsPDF } = window.jspdf || {};
        if (!jsPDF) {
            alert("PDF Generation Engine is loading. Please try again in a few seconds.");
            return;
        }

        const doc = new jsPDF({ unit: "mm", format: "a4" });
        const diag = state.lastDiagnosis;
        const nowStr = new Date().toLocaleString();

        // Header Background
        doc.setFillColor(15, 23, 42); // #0f172a
        doc.rect(0, 0, 210, 36, "F");

        // Brand Banner
        doc.setTextColor(16, 185, 129); // emerald
        doc.setFontSize(20);
        doc.setFont("helvetica", "bold");
        doc.text("PlantCare AI", 16, 16);

        doc.setFontSize(9);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(148, 163, 184); // slate-400
        doc.text("Precision Crop Pathology & Hyperlocal Agronomic Medicine Receipt", 16, 23);
        doc.text(`Official CIBRC Grounded Clinical Regimen • Generated: ${nowStr}`, 16, 29);

        // Watermark badge
        doc.setFillColor(16, 185, 129);
        doc.roundedRect(148, 10, 48, 16, 3, 3, "F");
        doc.setTextColor(2, 44, 34);
        doc.setFontSize(8);
        doc.setFont("helvetica", "bold");
        doc.text("CIBRC VERIFIED", 158, 17);
        doc.setFont("helvetica", "normal");
        doc.text("Standard Grounded", 157, 22);

        // Section 1: Pathology Diagnostic Summary
        let y = 48;
        doc.setTextColor(15, 23, 42);
        doc.setFontSize(13);
        doc.setFont("helvetica", "bold");
        doc.text("1. Diagnostic Pathology Findings", 16, y);

        y += 8;
        doc.setFillColor(248, 250, 252);
        doc.setDrawColor(226, 232, 240);
        doc.roundedRect(16, y, 178, 26, 2, 2, "FD");

        doc.setFontSize(9);
        doc.setTextColor(71, 85, 105);
        doc.setFont("helvetica", "normal");
        doc.text("Crop Category:", 22, y + 7);
        doc.text("Identified Disease:", 22, y + 14);
        doc.text("Scientific Pathogen:", 22, y + 21);

        doc.setTextColor(15, 23, 42);
        doc.setFont("helvetica", "bold");
        doc.text(diag.crop, 60, y + 7);
        doc.text(diag.disease_name, 60, y + 14);
        doc.setFont("helvetica", "italic");
        doc.text(diag.scientific_name, 60, y + 21);

        doc.setFont("helvetica", "normal");
        doc.setTextColor(71, 85, 105);
        doc.text("Model Confidence:", 118, y + 7);
        doc.text("Lesion Severity:", 118, y + 14);
        doc.text("Canopy Affected:", 118, y + 21);

        doc.setFont("helvetica", "bold");
        doc.setTextColor(16, 185, 129);
        doc.text(`${(diag.confidence_score * 100).toFixed(1)}%`, 155, y + 7);
        doc.setTextColor(234, 88, 12);
        doc.text(diag.severity, 155, y + 14);
        doc.text(`${diag.affected_percentage}%`, 155, y + 21);

        // Section 2: Immediate Containment Actions
        y += 34;
        doc.setTextColor(15, 23, 42);
        doc.setFontSize(13);
        doc.setFont("helvetica", "bold");
        doc.text("2. Immediate Containment Field Actions", 16, y);

        y += 5;
        doc.setFontSize(8.5);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(51, 65, 85);
        diag.immediate_actions.forEach((act, idx) => {
            y += 5;
            doc.text(`•  ${act}`, 20, y);
        });

        // Section 3: Dual-Track Prescriptions
        y += 10;
        doc.setFontSize(13);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(15, 23, 42);
        doc.text("3. Regulatory Prescribed Formulations (CIBRC / FAO Compliant)", 16, y);

        // Synthetic Chemistry Track
        y += 6;
        doc.setFillColor(254, 242, 242);
        doc.setDrawColor(254, 202, 202);
        doc.roundedRect(16, y, 86, 68, 2, 2, "FD");

        doc.setFontSize(10);
        doc.setTextColor(185, 28, 28);
        doc.setFont("helvetica", "bold");
        doc.text("🧪 Track A: Synthetic Chemistry", 20, y + 7);

        doc.setFontSize(8);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(71, 85, 105);
        let cy = y + 14;
        if (diag.chemical_treatments.length === 0) {
            doc.text("No synthetic chemicals required.", 20, cy);
        } else {
            const chem = diag.chemical_treatments[0];
            doc.setFont("helvetica", "bold");
            doc.setTextColor(15, 23, 42);
            doc.text(chem.name, 20, cy);
            cy += 5;
            doc.setFont("helvetica", "normal");
            doc.setTextColor(71, 85, 105);
            doc.text(`Active: ${chem.active_ingredient}`, 20, cy);
            cy += 5;
            doc.text(`Dosage/Acre: ${chem.dosage_per_acre}`, 20, cy);
            cy += 5;
            doc.text(`Dilution: ${chem.dilution_instructions || "Standard foliar spray"}`, 20, cy, { maxWidth: 78 });
            cy += 12;
            doc.setTextColor(185, 28, 28);
            doc.setFont("helvetica", "bold");
            doc.text(`Safety Waiting Period (PHI): ${chem.pre_harvest_interval_days} Days`, 20, cy);
        }

        // Organic / Bio-Control Track
        doc.setFillColor(240, 253, 244);
        doc.setDrawColor(187, 247, 208);
        doc.roundedRect(108, y, 86, 68, 2, 2, "FD");

        doc.setFontSize(10);
        doc.setTextColor(21, 128, 61);
        doc.setFont("helvetica", "bold");
        doc.text("🌿 Track B: Bio-Control / Organic", 112, y + 7);

        doc.setFontSize(8);
        let oy = y + 14;
        if (diag.organic_treatments.length === 0) {
            doc.text("Standard agronomic hygiene protocol.", 112, oy);
        } else {
            const org = diag.organic_treatments[0];
            doc.setFont("helvetica", "bold");
            doc.setTextColor(15, 23, 42);
            doc.text(org.name, 112, oy);
            oy += 5;
            doc.setFont("helvetica", "normal");
            doc.setTextColor(71, 85, 105);
            doc.text(`Active Agent: ${org.active_ingredient}`, 112, oy);
            oy += 5;
            doc.text(`Dosage/Acre: ${org.dosage_per_acre}`, 112, oy);
            oy += 5;
            doc.text(`Dilution: ${org.dilution_instructions || "Chlorine-free water spray"}`, 112, oy, { maxWidth: 78 });
            oy += 12;
            doc.setTextColor(21, 128, 61);
            doc.setFont("helvetica", "bold");
            doc.text("Certified Organic • 0-Day Waiting Period", 112, oy);
        }

        // Section 4: Retailer Reservation Token (If reserved)
        y += 76;
        if (state.lastReservation) {
            const r = state.lastReservation;
            doc.setFillColor(238, 242, 255);
            doc.setDrawColor(199, 210, 254);
            doc.roundedRect(16, y, 178, 30, 2, 2, "FD");

            doc.setTextColor(67, 56, 202);
            doc.setFontSize(10);
            doc.setFont("helvetica", "bold");
            doc.text(`🎟️ ACTIVE 4-HOUR RETAIL HOLD TOKEN: ${r.pickup_code}`, 22, y + 7);

            doc.setFontSize(8);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(71, 85, 105);
            doc.text(`Store: ${r.store_name} • Units Reserved: ${r.quantity_reserved} • Amount: ₹${r.total_price_inr.toFixed(2)}`, 22, y + 14);
            doc.text(`Expires at: ${r.expires_at} • Show pickup code at the counter for verified dispensary.`, 22, y + 21);
            y += 36;
        }

        // Legal & Regulatory Footer
        doc.setDrawColor(203, 213, 225);
        doc.line(16, 275, 194, 275);
        doc.setFontSize(7.5);
        doc.setTextColor(148, 163, 184);
        doc.text("PlantCare AI • Grounded Regulatory Agronomic Intelligence • Ministry of Agriculture & Farmers Welfare / CIBRC standards.", 16, 281);
        doc.text("Notice: Always adhere strictly to Pre-Harvest Interval (PHI) mandates before harvesting produce for commercial sale.", 16, 285);

        // Save PDF
        const filename = `PlantCare_Prescription_${diag.crop}_${diag.disease_name.replace(/\s+/g, '_')}.pdf`;
        doc.save(filename);
    });
}

function initPickupPdfGenerator() {
    const btn = document.getElementById("btnDownloadPickupPdf");
    if (!btn) return;

    btn.addEventListener("click", () => {
        if (!state.lastReservation) {
            alert("Please complete a 4-hour stock reservation first.");
            return;
        }

        const { jsPDF } = window.jspdf || {};
        if (!jsPDF) {
            alert("PDF Engine is loading. Please try again.");
            return;
        }

        const doc = new jsPDF({ unit: "mm", format: "a5" }); // A5 slip size
        const r = state.lastReservation;

        // Top Slip Header
        doc.setFillColor(15, 23, 42);
        doc.rect(0, 0, 148, 28, "F");

        doc.setTextColor(56, 189, 248);
        doc.setFontSize(16);
        doc.setFont("helvetica", "bold");
        doc.text("PlantCare AI", 12, 12);

        doc.setFontSize(8);
        doc.setTextColor(148, 163, 184);
        doc.setFont("helvetica", "normal");
        doc.text("Atomic 4-Hour Guaranteed Agro-Dealer Stock Slip", 12, 18);
        doc.text("Official Dispense Token & Anti-Counterfeit Receipt", 12, 23);

        // Big Pickup Code Box
        doc.setFillColor(241, 245, 249);
        doc.setDrawColor(56, 189, 248);
        doc.setLineWidth(0.8);
        doc.roundedRect(12, 34, 124, 26, 3, 3, "FD");

        doc.setTextColor(2, 132, 199);
        doc.setFontSize(22);
        doc.setFont("courier", "bold");
        doc.text(r.pickup_code, 74, 48, { align: "center" });

        doc.setFontSize(7.5);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(100, 116, 139);
        doc.text("CUSTOMER VERIFICATION PICKUP TOKEN", 74, 54, { align: "center" });

        // Reservation Ledger Details
        let y = 68;
        doc.setFontSize(8.5);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(71, 85, 105);

        const rows = [
            ["Reservation ID:", r.reservation_id],
            ["Customer Name:", r.farmer_name],
            ["Customer Phone:", r.farmer_phone],
            ["Agro-Dealer Store:", r.store_name],
            ["Target Medicine:", r.medicine_name],
            ["Quantity Held:", `${r.quantity_reserved} Units`],
            ["Total Payable (INR):", `₹${r.total_price_inr.toFixed(2)}`],
            ["Hold Expiration:", r.expires_at],
        ];

        rows.forEach(([lbl, val]) => {
            doc.setTextColor(71, 85, 105);
            doc.setFont("helvetica", "normal");
            doc.text(lbl, 14, y);
            doc.setTextColor(15, 23, 42);
            doc.setFont("helvetica", "bold");
            doc.text(String(val), 56, y);
            y += 7.5;
        });

        // Warning
        y += 4;
        doc.setFillColor(254, 243, 199);
        doc.setDrawColor(251, 191, 36);
        doc.roundedRect(12, y, 124, 16, 2, 2, "FD");
        doc.setTextColor(146, 64, 14);
        doc.setFontSize(7.2);
        doc.setFont("helvetica", "bold");
        doc.text("IMPORTANT DISPENSARY NOTE:", 16, y + 6);
        doc.setFont("helvetica", "normal");
        doc.text("Show this slip to the agro-dealer counter. If unclaimed within 4 hours, held stock", 16, y + 10);
        doc.text("automatically restocks to prevent retail lockouts.", 16, y + 13.5);

        // Download
        doc.save(`Pickup_Slip_${r.pickup_code}.pdf`);
    });
}
