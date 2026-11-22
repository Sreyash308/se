"""
Unit and Concurrency Tests for Spatial Inventory Routing & Reservation State Machine.
Verifies O(1) bounding-box pre-filtering, Haversine accuracy, proximity sorting,
and thread-safe atomic stock decrement.
"""

import threading
from datetime import datetime, timezone, timedelta
import pytest

from app.models.schemas import NearbyMedicinesRequest, MedicineReservationRequest
from app.models.entities import ReservationStatus
from app.services.spatial_inventory_service import SpatialInventoryService


class TestSpatialInventory:
    """Tests for geospatial query and inventory reservation lifecycle."""

    def test_haversine_formula_accuracy(self, clean_spatial_service):
        """Verifies mathematical accuracy of Haversine distance computation."""
        # Same point must yield 0.0 km
        dist_zero = clean_spatial_service.haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
        assert dist_zero == 0.0

        # Delhi (28.6139, 77.2090) to Gurugram (28.4595, 77.0266) is ~24.5 km
        dist_delhi_gurugram = clean_spatial_service.haversine_distance(
            28.6139, 77.2090, 28.4595, 77.0266
        )
        assert 22.0 <= dist_delhi_gurugram <= 27.0

    def test_bounding_box_calculation(self, clean_spatial_service):
        """Tests O(1) bounding box coordinate generation."""
        min_lat, max_lat, min_lon, max_lon = clean_spatial_service.calculate_bounding_box(
            lat=28.6139, lon=77.2090, radius_km=25.0
        )
        assert min_lat < 28.6139 < max_lat
        assert min_lon < 77.2090 < max_lon
        # Delta lat for 25km should be approx 25 / 111 = 0.225 degrees
        assert abs((max_lat - 28.6139) - (25.0 / 111.0)) < 0.01

    def test_nearby_medicines_within_radius(self, clean_spatial_service):
        """Verifies spatial pruning: nearby stores are included, distant stores excluded."""
        # Query near Delhi (28.6139, 77.2090) with 25km radius for Mancozeb
        req = NearbyMedicinesRequest(
            latitude=28.6139,
            longitude=77.2090,
            medicine_ids=["MED-MCZ-75"],
            radius_km=25.0,
            in_stock_only=True,
        )
        results = clean_spatial_service.find_nearby_medicines(req)
        assert len(results) > 0

        # Ensure all returned stores are <= 25.0 km
        for r in results:
            assert r.distance_km <= 25.0
            assert r.medicine_id == "MED-MCZ-75"
            assert r.stock_quantity > 0

        # Stores must be sorted by distance ascending
        distances = [r.distance_km for r in results]
        assert distances == sorted(distances)

        # Distant store (STR-007 in Meerut ~60km) must NOT be present in 25km radius
        store_ids = [r.store_id for r in results]
        assert "STR-007" not in store_ids

        # Expanding radius to 70km should include Meerut STR-007
        req_expanded = NearbyMedicinesRequest(
            latitude=28.6139,
            longitude=77.2090,
            medicine_ids=["MED-MCZ-75"],
            radius_km=70.0,
            in_stock_only=True,
        )
        results_expanded = clean_spatial_service.find_nearby_medicines(req_expanded)
        expanded_store_ids = [r.store_id for r in results_expanded]
        assert "STR-007" in expanded_store_ids

    def test_create_reservation_success_and_stock_decrement(self, clean_spatial_service):
        """Verifies atomic stock decrement upon reservation confirmation."""
        initial_stock = clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity
        assert initial_stock == 42

        req = MedicineReservationRequest(
            farmer_name="Ramesh Kumar",
            farmer_phone="+91-9988776655",
            store_id="STR-001",
            medicine_id="MED-MCZ-75",
            quantity_requested=2,
            reservation_hours=4,
        )
        res = clean_spatial_service.create_reservation(req)

        assert res.status == "CONFIRMED"
        assert res.quantity_reserved == 2
        assert res.pickup_code.startswith("PK-")
        assert res.reservation_id.startswith("RES-")

        # Verify stock was decremented atomically
        updated_stock = clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity
        assert updated_stock == initial_stock - 2

    def test_reservation_insufficient_stock_rejection(self, clean_spatial_service):
        """Rejects reservation requests exceeding available stock."""
        req = MedicineReservationRequest(
            farmer_name="Suresh Singh",
            farmer_phone="+91-9876543210",
            store_id="STR-001",
            medicine_id="MED-MCZ-75",
            quantity_requested=20,
            reservation_hours=4,
        )
        # First reservation consumes 20
        clean_spatial_service.create_reservation(req)
        # Second reservation consumes 20
        clean_spatial_service.create_reservation(req)
        # Remaining is 2; requesting 20 now should fail
        with pytest.raises(ValueError, match="Insufficient stock"):
            clean_spatial_service.create_reservation(req)

    def test_reservation_fulfillment(self, clean_spatial_service):
        """Verifies counter pickup code fulfillment."""
        req = MedicineReservationRequest(
            farmer_name="Amit Patel",
            farmer_phone="+91-9123456789",
            store_id="STR-001",
            medicine_id="MED-MCZ-75",
            quantity_requested=1,
            reservation_hours=4,
        )
        res = clean_spatial_service.create_reservation(req)

        record = clean_spatial_service.fulfill_reservation(res.pickup_code)
        assert record is not None
        assert record.status == ReservationStatus.FULFILLED

    def test_reservation_cancellation_and_restock(self, clean_spatial_service):
        """Verifies that cancelling an active reservation restores held inventory."""
        initial_stock = clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity

        req = MedicineReservationRequest(
            farmer_name="Vikas Yadav",
            farmer_phone="+91-9345678901",
            store_id="STR-001",
            medicine_id="MED-MCZ-75",
            quantity_requested=3,
            reservation_hours=4,
        )
        res = clean_spatial_service.create_reservation(req)
        assert clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity == initial_stock - 3

        cancelled = clean_spatial_service.cancel_reservation(res.reservation_id)
        assert cancelled is True
        # Restored to original stock
        assert clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity == initial_stock

    def test_reservation_auto_expiration_and_restock(self, clean_spatial_service):
        """Verifies that expired reservations are detected and held units returned to inventory."""
        initial_stock = clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity

        req = MedicineReservationRequest(
            farmer_name="Deepak Sharma",
            farmer_phone="+91-9876501234",
            store_id="STR-001",
            medicine_id="MED-MCZ-75",
            quantity_requested=4,
            reservation_hours=4,
        )
        res = clean_spatial_service.create_reservation(req)
        assert clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity == initial_stock - 4

        # Manually backdate expiration to 1 hour ago
        rec = clean_spatial_service.reservations[res.reservation_id]
        rec.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

        # Trigger expiration sweep
        expired_count = clean_spatial_service.expire_stale_reservations()
        assert expired_count >= 1
        assert rec.status == ReservationStatus.EXPIRED
        # Inventory restored
        assert clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity == initial_stock

    def test_reservation_uncarried_medicine_rejected(self, clean_spatial_service):
        """Verifies rejection when medicine is not carried by the specified store."""
        req = MedicineReservationRequest(
            farmer_name="Ramesh Kumar",
            farmer_phone="+91-9988776655",
            store_id="STR-001",
            medicine_id="MED-NONEXISTENT-999",
            quantity_requested=1,
            reservation_hours=4,
        )
        with pytest.raises(ValueError, match="is not carried by store"):
            clean_spatial_service.create_reservation(req)

    def test_cancel_nonexistent_reservation_returns_false(self, clean_spatial_service):
        """Verifies cancel_reservation returns False when reservation ID is invalid."""
        assert clean_spatial_service.cancel_reservation("RES-NONEXISTENT") is False

    def test_fulfill_nonexistent_pickup_code(self, clean_spatial_service):
        """Verifies fulfill_reservation returns None when pickup code is not found."""
        assert clean_spatial_service.fulfill_reservation("PK-UNKNOWN") is None

    def test_fulfill_already_fulfilled_reservation(self, clean_spatial_service):
        """Verifies second fulfillment returns existing record without error."""
        req = MedicineReservationRequest(
            farmer_name="Amit Patel",
            farmer_phone="+91-9123456789",
            store_id="STR-001",
            medicine_id="MED-MCZ-75",
            quantity_requested=1,
        )
        res = clean_spatial_service.create_reservation(req)
        first = clean_spatial_service.fulfill_reservation(res.pickup_code)
        assert first.status == ReservationStatus.FULFILLED
        second = clean_spatial_service.fulfill_reservation(res.pickup_code)
        assert second.status == ReservationStatus.FULFILLED

    def test_in_stock_only_filter_excludes_zero_stock(self, clean_spatial_service):
        """Verifies that items with zero stock are excluded when in_stock_only=True."""
        # Set stock of STR-001 for MED-MCZ-75 to 0
        clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity = 0

        req_filtered = NearbyMedicinesRequest(
            latitude=28.6139,
            longitude=77.2090,
            medicine_ids=["MED-MCZ-75"],
            radius_km=10.0,
            in_stock_only=True,
        )
        res_filtered = clean_spatial_service.find_nearby_medicines(req_filtered)
        assert not any(r.store_id == "STR-001" for r in res_filtered)

        # But when in_stock_only=False, it should appear with is_in_stock=False
        req_unfiltered = NearbyMedicinesRequest(
            latitude=28.6139,
            longitude=77.2090,
            medicine_ids=["MED-MCZ-75"],
            radius_km=10.0,
            in_stock_only=False,
        )
        res_unfiltered = clean_spatial_service.find_nearby_medicines(req_unfiltered)
        str001 = next((r for r in res_unfiltered if r.store_id == "STR-001"), None)
        assert str001 is not None
        assert str001.is_in_stock is False
        assert str001.stock_quantity == 0

    def test_concurrent_reservations_race_condition(self, clean_spatial_service):
        """
        Concurrency Stress Test:
        Simulates 25 concurrent threads attempting to reserve 2 units each
        against a store with stock of 42. Exactly 21 requests must succeed,
        4 must fail, and final stock must be exactly 0 (no negative stock).
        """
        initial_stock = clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity
        assert initial_stock == 42

        success_count = 0
        failure_count = 0
        lock = threading.Lock()

        def try_reserve():
            nonlocal success_count, failure_count
            req = MedicineReservationRequest(
                farmer_name="Concurrent Farmer",
                farmer_phone="+91-9876543210",
                store_id="STR-001",
                medicine_id="MED-MCZ-75",
                quantity_requested=2,
                reservation_hours=4,
            )
            try:
                clean_spatial_service.create_reservation(req)
                with lock:
                    success_count += 1
            except ValueError:
                with lock:
                    failure_count += 1

        threads = [threading.Thread(target=try_reserve) for _ in range(25)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 42 units / 2 units per request = 21 successful reservations
        assert success_count == 21
        assert failure_count == 4
        # Final stock must be strictly 0
        final_stock = clean_spatial_service.inventory[("STR-001", "MED-MCZ-75")].stock_quantity
        assert final_stock == 0
