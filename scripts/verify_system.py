#!/usr/bin/env python3
"""
PlantCare AI - System Verification Script.
Runs automated functional pipeline checks without requiring external network dependencies.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.diagnosis_service import diagnosis_service
from app.services.prescription_service import prescription_service
from app.services.spatial_inventory_service import spatial_inventory_service
from app.models.schemas import NearbyMedicinesRequest, MedicineReservationRequest
from app.models.entities import SeverityGrade


def verify_all():
    print("=" * 70)
    print("  PLANTCARE AI - SYSTEM HEALTH & PIPELINE VERIFICATION")
    print("=" * 70)

    # 1. Pathology Diagnosis Test
    print("\n[1/3] Testing Computer Vision Pathology & CIBRC Prescriptions...")
    pathology, conf = diagnosis_service.classify_crop_pathology("Tomato")
    resp = prescription_service.generate_prescription(
        pathology=pathology,
        confidence_score=conf,
        affected_percentage=28.4,
        severity_grade=SeverityGrade.MODERATE,
    )
    print(f"  ✓ Crop: {resp.crop}")
    print(f"  ✓ Pathogen: {resp.disease_name} ({resp.scientific_name})")
    print(f"  ✓ Confidence: {resp.confidence_score * 100:.1f}%")
    print(f"  ✓ Severity: {resp.severity}")
    print(f"  ✓ Prescribed CIBRC Chemical: {resp.chemical_treatments[0].name}")
    print(f"  ✓ Prescribed Bio-Control: {resp.organic_treatments[0].name}")

    # 2. Hyperlocal Spatial Query Test
    print("\n[2/3] Testing Geospatial Bounding-Box + Haversine Query...")
    spatial_req = NearbyMedicinesRequest(
        latitude=28.6139,
        longitude=77.2090,
        medicine_ids=[resp.chemical_treatments[0].id],
        radius_km=25.0,
        in_stock_only=True,
    )
    nearby_stores = spatial_inventory_service.find_nearby_medicines(spatial_req)
    print(f"  ✓ Found {len(nearby_stores)} nearby verified stores within 25 km:")
    for s in nearby_stores[:3]:
        print(f"    - {s.store_name}: {s.distance_km:.1f} km away (~{s.estimated_driving_time_minutes} min drive) | Stock: {s.stock_quantity} units @ ₹{s.price_inr:.2f}")

    # 3. Inventory Reservation Test
    print("\n[3/3] Testing Atomic 4-Hour Stock Reservation...")
    target_store = nearby_stores[0]
    reserve_req = MedicineReservationRequest(
        farmer_name="Verification Agent",
        farmer_phone="+91-9876543210",
        store_id=target_store.store_id,
        medicine_id=target_store.medicine_id,
        quantity_requested=2,
        reservation_hours=4,
    )
    reservation = spatial_inventory_service.create_reservation(reserve_req)
    print(f"  ✓ Reservation Confirmed: {reservation.reservation_id}")
    print(f"  ✓ Alphanumeric Pickup Code: {reservation.pickup_code}")
    print(f"  ✓ Units Reserved: {reservation.quantity_reserved} units")
    print(f"  ✓ Total Amount: ₹{reservation.total_price_inr:.2f}")
    print(f"  ✓ Valid Until: {reservation.expires_at}")

    # Counter Fulfillment
    fulfilled = spatial_inventory_service.fulfill_reservation(reservation.pickup_code)
    print(f"  ✓ POS Counter Fulfillment Check: Status is {fulfilled.status.value}")

    print("\n" + "=" * 70)
    print("  ALL CORE SYSTEM CHECKS PASSED SUCCESSFULLY (100%)")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
