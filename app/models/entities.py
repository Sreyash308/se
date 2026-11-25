"""
Domain Entities and Enumerations for PlantCare AI.
Encapsulates domain invariants, pathology classes, and relational models.
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CropType(str, Enum):
    """Supported agricultural crop classifications."""
    TOMATO = "Tomato"
    POTATO = "Potato"
    CORN = "Corn"
    APPLE = "Apple"
    GRAPE = "Grape"
    RICE = "Rice"
    BELL_PEPPER = "Bell Pepper"
    COTTON = "Cotton"
    BLUEBERRY = "Blueberry"
    CHERRY = "Cherry"
    ORANGE = "Orange"
    PEACH = "Peach"
    RASPBERRY = "Raspberry"
    SOYBEAN = "Soybean"
    SQUASH = "Squash"
    STRAWBERRY = "Strawberry"


class SeverityGrade(str, Enum):
    """Foliar lesion surface area severity grades."""
    HEALTHY = "Healthy (0.0% leaf surface affected)"
    MILD = "Mild (< 15.0% leaf surface affected)"
    MODERATE = "Moderate (15% - 40% leaf surface affected)"
    SEVERE = "Severe (> 40.0% leaf surface affected)"

    @classmethod
    def from_percentage(cls, pct: float) -> "SeverityGrade":
        """Deterministic boundary mapping following Boundary Value Analysis (BVA)."""
        if pct <= 0.0:
            return cls.HEALTHY
        elif pct < 15.0:
            return cls.MILD
        elif pct <= 40.0:
            return cls.MODERATE
        else:
            return cls.SEVERE


class PathogenType(str, Enum):
    """Biological taxonomy of plant pathogens."""
    FUNGAL_ASCOMYCOTA = "Fungal Ascomycota"
    FUNGAL_OOMYCOTA = "Fungal Oomycota (Water Mold)"
    FUNGAL_BASIDIOMYCOTA = "Fungal Basidiomycota"
    BACTERIAL = "Bacterial Pathogen"
    VIRAL = "Plant Viral Complex"
    ABIOTIC = "Abiotic Nutritional Disorder"
    PHYSIOLOGICAL = "None / Healthy Tissue"
    ARTHROPOD = "Foliar Mite / Arthropod Pest"


class ReservationStatus(str, Enum):
    """Status lifecycle of an inventory hold reservation."""
    CONFIRMED = "CONFIRMED"
    FULFILLED = "FULFILLED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class MedicineItem(BaseModel):
    """Agrochemical or bio-pesticide formulation details."""
    id: str
    name: str
    active_ingredient: str
    concentration: str
    is_organic: bool
    dosage_per_acre: str
    dilution_instructions: str
    safety_waiting_period_days: int = Field(description="Pre-Harvest Interval (PHI)")
    regulatory_cibrc_approved: bool = True
    target_pathogens: List[str] = Field(default_factory=list)


class DiseasePathology(BaseModel):
    """Agronomic disease pathology profile."""
    disease_id: str
    crop: CropType
    common_name: str
    scientific_name: str
    pathogen_type: PathogenType
    key_symptoms: List[str]
    immediate_actions: List[str]
    chemical_medicine_ids: List[str]
    organic_medicine_ids: List[str]
    preventive_measures: List[str]


class StoreEntity(BaseModel):
    """Physical agro-dealer retail outlet entity."""
    store_id: str
    store_name: str
    government_license_number: str
    contact_phone: str
    physical_address: str
    latitude: float
    longitude: float
    is_verified: bool = True
    operating_hours: str = "08:00 AM - 07:30 PM (Mon-Sat)"


class InventoryRecord(BaseModel):
    """Store inventory ledger line item."""
    store_id: str
    medicine_id: str
    stock_quantity: int
    unit_packaging: str
    unit_price_inr: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReservationRecord(BaseModel):
    """Time-bounded atomic inventory reservation."""
    reservation_id: str
    farmer_name: str
    farmer_phone: str
    store_id: str
    store_name: str
    medicine_id: str
    medicine_name: str
    quantity_reserved: int
    unit_price_inr: float
    total_price_inr: float
    status: ReservationStatus = ReservationStatus.CONFIRMED
    reserved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    pickup_code: str
