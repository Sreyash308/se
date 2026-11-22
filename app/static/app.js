/**
 * PlantCare AI - Frontend Client Orchestration
 * Handles leaf image preprocessing, API calls, spatial query rendering,
 * and atomic stock reservation workflows.
 */

// ---------------------------------------------------------------------------
// 1. Synthetic Leaf Sample Generators (Rendered as Base64 JPEG)
// ---------------------------------------------------------------------------

function createSyntheticLeafSample(patternType) {
    const canvas = document.createElement("canvas");
    canvas.width = 224;
    canvas.height = 224;
    const ctx = canvas.getContext("2d");

    // Leaf Background Gradient (Green vegetative tissue)
    const bgGrad = ctx.createRadialGradient(112, 112, 30, 112, 112, 110);
    bgGrad.addColorStop(0, "#4ade80");
    bgGrad.addColorStop(0.7, "#16a34a");
    bgGrad.addColorStop(1, "#14532d");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, 224, 224);

    // Leaf midrib and vein structure
    ctx.strokeStyle = "#86efac";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(112, 220);
    ctx.quadraticCurveTo(115, 112, 112, 10);
    ctx.stroke();

    ctx.lineWidth = 1.5;
    for (let y = 40; y < 200; y += 30) {
        ctx.beginPath();
        ctx.moveTo(112, y);
        ctx.lineTo(40, y - 20);
        ctx.moveTo(112, y);
        ctx.lineTo(184, y - 20);
        ctx.stroke();
    }

    if (patternType === "tomato_early_blight") {
        // Concentric target-board brown lesions with chlorotic yellow halo
        const spots = [
            { x: 80, y: 70, r: 24 },
            { x: 140, y: 130, r: 28 },
            { x: 75, y: 160, r: 18 }
        ];
        spots.forEach(s => {
            // Chlorotic yellow halo
            ctx.fillStyle = "rgba(234, 179, 8, 0.75)";
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r + 8, 0, Math.PI * 2);
            ctx.fill();

            // Concentric brown rings
            ctx.fillStyle = "#78350f";
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = "#451a03";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 0.6, 0, Math.PI * 2);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 0.25, 0, Math.PI * 2);
            ctx.stroke();
        });
    } else if (patternType === "potato_late_blight") {
        // Irregular dark water-soaked lesions spreading across margin
        ctx.fillStyle = "#292524";
        ctx.beginPath();
        ctx.moveTo(30, 20);
        ctx.bezierCurveTo(90, 40, 70, 110, 20, 120);
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(150, 120);
        ctx.bezierCurveTo(220, 140, 200, 210, 130, 200);
        ctx.fill();

        // White downy mildew margin
        ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
        ctx.lineWidth = 2.5;
        ctx.stroke();
    } else if (patternType === "rice_blast") {
        // Spindle diamond-shaped lesions with gray centers
        const lesions = [
            { x: 100, y: 60 },
            { x: 130, y: 120 },
            { x: 85, y: 170 }
        ];
        lesions.forEach(l => {
            ctx.fillStyle = "#7c2d12";
            ctx.beginPath();
            ctx.ellipse(l.x, l.y, 20, 6, Math.PI / 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = "#e2e8f0";
            ctx.beginPath();
            ctx.ellipse(l.x, l.y, 10, 3, Math.PI / 4, 0, Math.PI * 2);
            ctx.fill();
        });
    }
    // "healthy_corn" keeps clean green canopy with no spots

    return canvas.toDataURL("image/jpeg", 0.9);
}

// ---------------------------------------------------------------------------
// 2. Application State
// ---------------------------------------------------------------------------

const state = {
    selectedCrop: "Tomato",
    currentImageBase64: createSyntheticLeafSample("tomato_early_blight"),
    lastDiagnosis: null,
    searchRadius: 25.0,
    userLocation: { lat: 28.6139, lon: 77.2090 },
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

    // Initial leaf preview
    const preview = document.getElementById("imagePreview");
    if (preview) {
        preview.src = state.currentImageBase64;
    }
});

// ---------------------------------------------------------------------------
// 4. Tab Navigation
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

            const base64Data = createSyntheticLeafSample(sampleKey);
            state.currentImageBase64 = base64Data;
            preview.src = base64Data;
            previewInfo.textContent = `Sample: ${btn.textContent}`;
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
// 6. Pathology Diagnosis & Prescription Execution
// ---------------------------------------------------------------------------

function initDiagnosisRunner() {
    const btn = document.getElementById("btnRunDiagnosis");
    const btnFindStores = document.getElementById("btnFindStoresForPrescription");

    btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.textContent = "⏳ Running Deep Computer Vision Inference...";

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
            renderDiagnosisResults(data);
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
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

function renderDiagnosisResults(data) {
    document.getElementById("diagPlaceholder").classList.add("hidden");
    const resBox = document.getElementById("diagResults");
    resBox.classList.remove("hidden");

    document.getElementById("resCrop").textContent = data.crop;
    document.getElementById("resDisease").textContent = data.disease_name;
    document.getElementById("resScientific").textContent = data.scientific_name;
    document.getElementById("resConfidence").querySelector(".conf-num").textContent =
        `${(data.confidence_score * 100).toFixed(1)}%`;

    document.getElementById("resSeverity").textContent =
        `${data.severity} (${data.affected_percentage}% affected)`;
    document.getElementById("resSeverityBar").style.width = `${Math.min(100, Math.max(5, data.affected_percentage))}%`;

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
}

// ---------------------------------------------------------------------------
// 7. Hyperlocal Spatial Inventory Routing
// ---------------------------------------------------------------------------

function initSpatialSearch() {
    const btnSearch = document.getElementById("btnSearchStores");
    const radiusSlider = document.getElementById("inputRadius");
    const radiusLabel = document.getElementById("radiusLabel");
    const btnGps = document.getElementById("btnUseGps");
    const presets = document.querySelectorAll(".coord-preset");

    radiusSlider.addEventListener("input", (e) => {
        radiusLabel.textContent = `${e.target.value} km`;
        state.searchRadius = parseFloat(e.target.value);
    });

    presets.forEach(p => {
        p.addEventListener("click", () => {
            document.getElementById("inputLat").value = p.getAttribute("data-lat");
            document.getElementById("inputLon").value = p.getAttribute("data-lon");
        });
    });

    btnGps.addEventListener("click", () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            pos => {
                document.getElementById("inputLat").value = pos.coords.latitude.toFixed(4);
                document.getElementById("inputLon").value = pos.coords.longitude.toFixed(4);
            },
            err => alert(`Unable to acquire GPS coordinates: ${err.message}`)
        );
    });

    btnSearch.addEventListener("click", async () => {
        btnSearch.disabled = true;
        btnSearch.textContent = "⚡ Running Spatial Bounding-Box & Haversine Query...";

        const lat = parseFloat(document.getElementById("inputLat").value);
        const lon = parseFloat(document.getElementById("inputLon").value);
        const radius = parseFloat(radiusSlider.value);
        const medId = document.getElementById("selectMedicine").value;
        const inStockOnly = document.getElementById("checkInStockOnly").checked;

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
        } catch (error) {
            alert(`Spatial Error: ${error.message}`);
        } finally {
            btnSearch.disabled = false;
            btnSearch.textContent = "⚡ Execute Hyperlocal Geospatial Inventory Query";
        }
    });
}

function renderStoreResults(stores) {
    const tbody = document.getElementById("storesTableBody");
    const subtitle = document.getElementById("storeCountSubtitle");
    tbody.innerHTML = "";

    subtitle.textContent = `Found ${stores.length} verified in-stock dealer(s) within selected radius`;

    if (stores.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    No verified stores with active stock within this radius. Try increasing search radius (e.g. 50 km).
                </td>
            </tr>
        `;
        return;
    }

    stores.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <strong>${s.store_name}</strong>
                <div class="text-muted" style="font-size:0.75rem;">${s.store_address} • 📞 ${s.store_phone}</div>
            </td>
            <td><strong>${s.distance_km.toFixed(1)} km</strong></td>
            <td>~${s.estimated_driving_time_minutes} min</td>
            <td>
                <span class="crop-tag">${s.medicine_id}</span>
                <div style="font-size:0.8rem;">${s.medicine_name}</div>
            </td>
            <td>
                <span class="badge ${s.stock_quantity > 10 ? 'badge-green' : 'badge-orange'}">
                    ${s.stock_quantity} In Stock (${s.unit_type})
                </span>
            </td>
            <td><strong>₹${s.price_inr.toFixed(2)}</strong></td>
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
                <div style="font-size:0.75rem; color:var(--gray-600); margin-top:4px;">${s.physical_address}</div>
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
