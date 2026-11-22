"""
FastAPI REST API End-to-End Integration Tests.
Verifies all public endpoints, parameter validation, schema compliance,
and HTTP status codes conforming to OpenAPI 3.0.
"""

import io
from PIL import Image


class TestAPIEndpoints:
    """End-to-end integration tests for FastAPI router endpoints."""

    def test_health_endpoint(self, client):
        """Verifies GET /api/v1/health telemetry response."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert data["registered_stores"] >= 8
        assert data["catalog_medicines"] >= 10
        assert data["supported_crops"] >= 6

    def test_diagnose_api_post(self, client, valid_leaf_image_base64):
        """Verifies POST /api/v1/diagnose with valid base64 payload."""
        payload = {
            "crop_type": "Tomato",
            "image_base64": valid_leaf_image_base64,
        }
        response = client.post("/api/v1/diagnose", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "Tomato"
        assert "disease_name" in data
        assert "confidence_score" in data
        assert "severity" in data
        assert "chemical_treatments" in data
        assert "organic_treatments" in data

    def test_diagnose_api_default_sample(self, client):
        """Verifies POST /api/v1/diagnose without image uses benchmark sample."""
        payload = {"crop_type": "Tomato"}
        response = client.post("/api/v1/diagnose", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "Tomato"
        assert data["disease_name"] == "Early Blight"
        assert data["affected_percentage"] == 28.4
        assert len(data["chemical_treatments"]) > 0

    def test_diagnose_api_invalid_base64(self, client):
        """Verifies POST /api/v1/diagnose rejects corrupt base64 string with 400."""
        payload = {
            "crop_type": "Tomato",
            "image_base64": "invalid_base64_string!!!",
        }
        response = client.post("/api/v1/diagnose", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_diagnose_multipart_file_upload(self, client):
        """Verifies POST /api/v1/diagnose/upload binary multipart stream."""
        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        response = client.post(
            "/api/v1/diagnose/upload",
            files={"file": ("leaf.jpg", buf, "image/jpeg")},
            data={"crop_type": "Tomato"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "Tomato"

    def test_nearby_medicines_api(self, client):
        """Verifies POST /api/v1/medicines/nearby returns proximity-sorted stores."""
        payload = {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "medicine_ids": ["MED-MCZ-75"],
            "radius_km": 25.0,
            "in_stock_only": True,
        }
        response = client.post("/api/v1/medicines/nearby", json=payload)
        assert response.status_code == 200
        stores = response.json()
        assert isinstance(stores, list)
        assert len(stores) > 0
        assert stores[0]["store_id"] == "STR-001"
        assert stores[0]["is_in_stock"] is True

    def test_nearby_medicines_empty_ids_rejected(self, client):
        """Rejects request with empty medicine_ids list with 400 Bad Request."""
        payload = {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "medicine_ids": [],
            "radius_km": 25.0,
        }
        response = client.post("/api/v1/medicines/nearby", json=payload)
        assert response.status_code == 400

    def test_nearby_medicines_out_of_bounds_coords(self, client):
        """Rejects out-of-bounds latitude (>90) with 422 Unprocessable Entity."""
        payload = {
            "latitude": 95.0,
            "longitude": 77.2090,
            "medicine_ids": ["MED-MCZ-75"],
            "radius_km": 25.0,
        }
        response = client.post("/api/v1/medicines/nearby", json=payload)
        assert response.status_code == 422

    def test_reservation_lifecycle_api(self, client):
        """Verifies POST /api/v1/medicines/reserve, lookup, and POS counter fulfillment."""
        reserve_payload = {
            "farmer_name": "Ramesh Kumar",
            "farmer_phone": "+91-9988776655",
            "store_id": "STR-001",
            "medicine_id": "MED-MCZ-75",
            "quantity_requested": 2,
            "reservation_hours": 4,
        }
        # 1. Create reservation
        res_post = client.post("/api/v1/medicines/reserve", json=reserve_payload)
        assert res_post.status_code == 200
        res_data = res_post.json()
        res_id = res_data["reservation_id"]
        pickup_code = res_data["pickup_code"]
        assert res_data["status"] == "CONFIRMED"
        assert res_data["quantity_reserved"] == 2

        # 2. Lookup reservation
        get_res = client.get(f"/api/v1/reservations/{res_id}")
        assert get_res.status_code == 200
        record = get_res.json()
        assert record["reservation_id"] == res_id
        assert record["status"] == "CONFIRMED"

        # 3. Fulfill pickup at counter
        fulfill_res = client.post(f"/api/v1/reservations/fulfill/{pickup_code}")
        assert fulfill_res.status_code == 200
        fulfill_data = fulfill_res.json()
        assert fulfill_data["status"] == "success"
        assert fulfill_data["reservation"]["status"] == "FULFILLED"

    def test_reservation_invalid_phone(self, client):
        """Rejects phone number with fewer than 10 digits with 422."""
        payload = {
            "farmer_name": "Ramesh",
            "farmer_phone": "123",
            "store_id": "STR-001",
            "medicine_id": "MED-MCZ-75",
            "quantity_requested": 2,
        }
        response = client.post("/api/v1/medicines/reserve", json=payload)
        assert response.status_code == 422

    def test_reservation_nonexistent_store(self, client):
        """Rejects reservation for non-existent store with 400."""
        payload = {
            "farmer_name": "Ramesh Kumar",
            "farmer_phone": "+91-9988776655",
            "store_id": "STR-NONEXISTENT",
            "medicine_id": "MED-MCZ-75",
            "quantity_requested": 2,
        }
        response = client.post("/api/v1/medicines/reserve", json=payload)
        assert response.status_code == 400

    def test_reservation_lookup_nonexistent_returns_404(self, client):
        """Verifies GET /api/v1/reservations/{non_existent} returns 404."""
        response = client.get("/api/v1/reservations/RES-NONEXISTENT")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_reservation_fulfillment_nonexistent_returns_404(self, client):
        """Verifies POST /api/v1/reservations/fulfill/{non_existent} returns 404."""
        response = client.post("/api/v1/reservations/fulfill/PK-INVALID99")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_diagnose_multipart_oversized_file(self, client, monkeypatch):
        """Verifies file upload exceeding MAX_IMAGE_SIZE_MB is rejected with 400."""
        from app.config import settings
        monkeypatch.setattr(settings, "MAX_IMAGE_SIZE_MB", 0.0001)

        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        response = client.post(
            "/api/v1/diagnose/upload",
            files={"file": ("leaf.jpg", buf, "image/jpeg")},
            data={"crop_type": "Tomato"},
        )
        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"].lower()

    def test_get_stores_and_catalog_api(self, client):
        """Verifies catalog list endpoints."""
        stores_resp = client.get("/api/v1/stores")
        assert stores_resp.status_code == 200
        assert len(stores_resp.json()) >= 8

        catalog_resp = client.get("/api/v1/catalog")
        assert catalog_resp.status_code == 200
        assert len(catalog_resp.json()) >= 10

    def test_root_serves_html(self, client):
        """Verifies GET / serves the interactive HTML5 client."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "PlantCare AI" in response.text
