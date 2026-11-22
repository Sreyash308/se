"""
Pydantic v2 Request & Response Data Transfer Objects (DTOs).
Strict schema validation with OpenAPI examples matching SRS.md and README.md.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DiagnosisRequest(BaseModel):
    """Payload for leaf disease diagnosis."""
    crop_type: Optional[str] = Field(
        default="Tomato",
        description="Target agricultural crop name (e.g., Tomato, Potato, Corn, Apple, Rice)"
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded RGB foliar image string or data URI"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "crop_type": "Tomato",
                "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
            }
        }
    }


class TreatmentInfo(BaseModel):
    """Detailed agronomic recommendation item."""
    id: str
    name: str
    active_ingredient: str
    dosage_per_acre: str
    dilution_instructions: Optional[str] = None
    pre_harvest_interval_days: Optional[int] = Field(
        default=None,
        description="Safety waiting period before crop harvest in days"
    )


class DiagnosisResponse(BaseModel):
    """Standard response model for foliar disease classification."""
    crop: str
    disease_name: str
    scientific_name: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    severity: str
    affected_percentage: float = Field(ge=0.0, le=100.0)
    pathogen_type: str
    key_symptoms: List[str]
    immediate_actions: List[str]
    chemical_treatments: List[TreatmentInfo]
    organic_treatments: List[TreatmentInfo]
    preventive_measures: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "crop": "Tomato",
                "disease_name": "Early Blight",
                "scientific_name": "Alternaria solani",
                "confidence_score": 0.954,
                "severity": "Moderate (15% - 40% leaf surface affected)",
                "affected_percentage": 28.4,
                "pathogen_type": "Fungal Ascomycota",
                "key_symptoms": [
                    "Concentric ring dark brown spots (target-board pattern) on older lower leaves",
                    "Yellow halo chlorosis surrounding necrotic leaf spots"
                ],
                "immediate_actions": [
                    "Immediately prune and safely destroy infected lower leaves (do not compost).",
                    "Avoid overhead sprinkler irrigation to keep the canopy dry."
                ],
                "chemical_treatments": [
                    {
                        "id": "MED-MCZ-75",
                        "name": "Mancozeb 75% WP",
                        "active_ingredient": "Mancozeb",
                        "dosage_per_acre": "600-800 grams",
                        "dilution_instructions": "Dissolve 2-2.5g in 1 liter of clean water.",
                        "pre_harvest_interval_days": 7
                    }
                ],
                "organic_treatments": [
                    {
                        "id": "MED-TRI-VIR",
                        "name": "Trichoderma viride 1% WP",
                        "active_ingredient": "Trichoderma viride",
                        "dosage_per_acre": "1000 grams",
                        "dilution_instructions": "Mix 5g/liter with farmyard manure or spray directly.",
                        "pre_harvest_interval_days": 0
                    }
                ],
                "preventive_measures": [
                    "Implement a minimum 3-year crop rotation with non-solanaceous crops."
                ]
            }
        }
    }


class NearbyMedicinesRequest(BaseModel):
    """Payload to search nearby registered agro-dealers stocking prescribed inputs."""
    latitude: float = Field(ge=-90.0, le=90.0, description="Farmer GPS latitude")
    longitude: float = Field(ge=-180.0, le=180.0, description="Farmer GPS longitude")
    medicine_ids: List[str] = Field(description="Prescribed medicine IDs to check in stock")
    radius_km: float = Field(default=25.0, ge=1.0, le=100.0, description="Radial search distance in km")
    in_stock_only: bool = Field(default=True, description="Filter out zero-stock inventory records")

    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "medicine_ids": ["MED-MCZ-75"],
                "radius_km": 25.0,
                "in_stock_only": True
            }
        }
    }


class StoreAvailabilityResponse(BaseModel):
    """Proximity-ranked store inventory availability record."""
    store_id: str
    store_name: str
    store_phone: str
    store_address: str
    distance_km: float
    medicine_id: str
    medicine_name: str
    stock_quantity: int
    unit_type: str
    price_inr: float
    is_in_stock: bool
    estimated_driving_time_minutes: int


class MedicineReservationRequest(BaseModel):
    """Payload to create a 4-hour inventory hold."""
    farmer_name: str = Field(min_length=2, max_length=100)
    farmer_phone: str = Field(min_length=10, max_length=20)
    store_id: str
    medicine_id: str
    quantity_requested: int = Field(ge=1, le=20, description="Maximum 20 units per reservation")
    reservation_hours: int = Field(default=4, ge=1, le=12)

    @field_validator("farmer_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = "".join(ch for ch in v if ch.isdigit() or ch in ("+", "-"))
        if len(cleaned) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        return v


class MedicineReservationResponse(BaseModel):
    """Confirmation payload with pickup token for inventory hold."""
    reservation_id: str
    status: str
    store_name: str
    medicine_name: str
    quantity_reserved: int
    total_price_inr: float
    expires_at: str
    pickup_code: str


class HealthResponse(BaseModel):
    """Application healthcheck telemetry response."""
    status: str = "ok"
    version: str = "1.0.0"
    service: str = "PlantCare AI Gateway"
    uptime_status: str = "healthy"
    registered_stores: int
    catalog_medicines: int
    supported_crops: int
