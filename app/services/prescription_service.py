"""
Agronomic Prescription Service.
Deterministic CIBRC Expert Rule Engine that translates crop pathology
and foliar severity grades into regulatory-compliant dual-track prescriptions.
"""

from typing import List, Optional
from app.models.entities import SeverityGrade, DiseasePathology
from app.models.schemas import TreatmentInfo, DiagnosisResponse
from app.services.agronomic_database import MEDICINES_CATALOG


class PrescriptionService:
    """Expert Rule Engine adhering strictly to CIBRC agricultural regulations."""

    @classmethod
    def generate_prescription(
        cls,
        pathology: DiseasePathology,
        confidence_score: float,
        affected_percentage: float,
        severity_grade: SeverityGrade,
    ) -> DiagnosisResponse:
        """
        Formulates dual therapeutic regimens:
        - Synthetic Curative / Protective Agrochemicals (if disease present and severity > 0)
        - Certified Organic / Biological Antagonists
        Guarantees zero chemical prescriptions for healthy foliar canopies.
        """
        chemical_treatments: List[TreatmentInfo] = []
        organic_treatments: List[TreatmentInfo] = []

        is_healthy = (
            severity_grade == SeverityGrade.HEALTHY
            or affected_percentage <= 0.0
            or "healthy" in pathology.common_name.lower()
        )

        # 1. Chemical Treatment Rule Resolution
        if not is_healthy:
            for med_id in pathology.chemical_medicine_ids:
                med = MEDICINES_CATALOG.get(med_id)
                if med and med.regulatory_cibrc_approved:
                    chemical_treatments.append(
                        TreatmentInfo(
                            id=med.id,
                            name=med.name,
                            active_ingredient=med.active_ingredient,
                            dosage_per_acre=med.dosage_per_acre,
                            dilution_instructions=med.dilution_instructions,
                            pre_harvest_interval_days=med.safety_waiting_period_days,
                        )
                    )

        # 2. Organic / Biological Treatment Rule Resolution
        for med_id in pathology.organic_medicine_ids:
            med = MEDICINES_CATALOG.get(med_id)
            if med and med.regulatory_cibrc_approved:
                organic_treatments.append(
                    TreatmentInfo(
                        id=med.id,
                        name=med.name,
                        active_ingredient=med.active_ingredient,
                        dosage_per_acre=med.dosage_per_acre,
                        dilution_instructions=med.dilution_instructions,
                        pre_harvest_interval_days=med.safety_waiting_period_days,
                    )
                )

        # Formulate full response conforming to Pydantic v2 schema
        return DiagnosisResponse(
            crop=pathology.crop.value if hasattr(pathology.crop, "value") else str(pathology.crop),
            disease_name=pathology.common_name,
            scientific_name=pathology.scientific_name,
            confidence_score=round(confidence_score, 3),
            severity=severity_grade.value if hasattr(severity_grade, "value") else str(severity_grade),
            affected_percentage=round(affected_percentage, 1),
            pathogen_type=pathology.pathogen_type.value if hasattr(pathology.pathogen_type, "value") else str(pathology.pathogen_type),
            key_symptoms=pathology.key_symptoms,
            immediate_actions=pathology.immediate_actions,
            chemical_treatments=chemical_treatments,
            organic_treatments=organic_treatments,
            preventive_measures=pathology.preventive_measures,
        )


prescription_service = PrescriptionService()
