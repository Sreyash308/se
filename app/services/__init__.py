"""
Services package for PlantCare AI.
"""

from app.services.agronomic_database import (
    MEDICINES_CATALOG,
    DISEASE_CATALOG,
    STORE_CATALOG,
    INITIAL_INVENTORY,
)
from app.services.diagnosis_service import diagnosis_service, DiagnosisService
from app.services.prescription_service import prescription_service, PrescriptionService
from app.services.spatial_inventory_service import (
    spatial_inventory_service,
    SpatialInventoryService,
)

__all__ = [
    "MEDICINES_CATALOG",
    "DISEASE_CATALOG",
    "STORE_CATALOG",
    "INITIAL_INVENTORY",
    "diagnosis_service",
    "DiagnosisService",
    "prescription_service",
    "PrescriptionService",
    "spatial_inventory_service",
    "SpatialInventoryService",
]
