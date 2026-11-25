"""
Unit and Integration Tests for Foliar Diagnosis & Prescription Engine.
Enforces Equivalence Partitioning (EP), Boundary Value Analysis (BVA),
and CIBRC regulatory prescription rules.
"""

import base64
import pytest
from PIL import Image

from app.models.entities import SeverityGrade, CropType
from app.services.diagnosis_service import diagnosis_service
from app.services.prescription_service import prescription_service
from app.services.agronomic_database import DISEASE_CATALOG


class TestDiagnosisAndSeverity:
    """Tests for Computer Vision image processing and severity quantification."""

    def test_diagnose_tomato_early_blight_default(self):
        """Verifies default benchmark classification for Tomato Early Blight."""
        pathology, conf = diagnosis_service.classify_crop_pathology("Tomato")
        assert pathology.crop == CropType.TOMATO
        assert pathology.common_name == "Early Blight"
        assert conf >= 0.70

        # Formulate prescription
        resp = prescription_service.generate_prescription(
            pathology=pathology,
            confidence_score=conf,
            affected_percentage=28.4,
            severity_grade=SeverityGrade.MODERATE,
        )
        assert resp.crop == "Tomato"
        assert resp.disease_name == "Early Blight"
        assert resp.severity == SeverityGrade.MODERATE.value
        assert len(resp.chemical_treatments) > 0
        assert any(t.id == "MED-MCZ-75" for t in resp.chemical_treatments)
        assert len(resp.organic_treatments) > 0

    def test_diagnose_healthy_crop_severity(self):
        """
        Critical Non-Negotiable Invariant:
        Healthy crops MUST NOT be prescribed synthetic chemical fungicides.
        """
        pathology, conf = diagnosis_service.classify_crop_pathology("Tomato", severity_pct=0.0)
        assert "Healthy" in pathology.common_name

        resp = prescription_service.generate_prescription(
            pathology=pathology,
            confidence_score=conf,
            affected_percentage=0.0,
            severity_grade=SeverityGrade.HEALTHY,
        )
        assert resp.severity == SeverityGrade.HEALTHY.value
        assert resp.affected_percentage == 0.0
        # Synthetic chemical treatments must be strictly empty
        assert len(resp.chemical_treatments) == 0
        # Prophylactic organic tonic must be available
        assert len(resp.organic_treatments) > 0
        assert resp.organic_treatments[0].id == "MED-BIO-NIL"

    @pytest.mark.parametrize(
        "percentage,expected_grade",
        [
            (0.0, SeverityGrade.HEALTHY),
            (5.0, SeverityGrade.MILD),
            (14.9, SeverityGrade.MILD),
            (15.0, SeverityGrade.MODERATE),
            (25.0, SeverityGrade.MODERATE),
            (39.9, SeverityGrade.MODERATE),
            (40.0, SeverityGrade.MODERATE),
            (40.1, SeverityGrade.SEVERE),
            (65.0, SeverityGrade.SEVERE),
        ],
    )
    def test_severity_boundary_value_analysis(self, percentage, expected_grade):
        """Boundary Value Analysis (BVA) for severity transitions."""
        grade = SeverityGrade.from_percentage(percentage)
        assert grade == expected_grade

    def test_image_preprocessing_tensor_shape(self, valid_leaf_image_base64):
        """Verifies image ingestion, decoding, and 224x224x3 ImageNet tensor output."""
        img = diagnosis_service.decode_and_validate_image(valid_leaf_image_base64)
        assert img.size == (224, 224)

        tensor = diagnosis_service.preprocess_tensor(img)
        # Tensor must be (3, 224, 224)
        assert tensor.shape == (3, 224, 224)
        assert tensor.dtype.name == "float32"

    def test_lesion_severity_segmentation(self, lesion_leaf_image_base64):
        """Tests HSV necrotic surface area percentage computation."""
        img = diagnosis_service.decode_and_validate_image(lesion_leaf_image_base64)
        pct, grade = diagnosis_service.quantify_lesion_severity(img)
        assert isinstance(pct, float)
        assert pct >= 0.0
        assert isinstance(grade, SeverityGrade)

    def test_lesion_severity_override(self, valid_leaf_image_base64):
        """Tests manual default_override parameter in quantify_lesion_severity."""
        img = diagnosis_service.decode_and_validate_image(valid_leaf_image_base64)
        pct, grade = diagnosis_service.quantify_lesion_severity(img, default_override=12.5)
        assert pct == 12.5
        assert grade == SeverityGrade.MILD

    def test_lesion_severity_uniform_background_fallback(self):
        """Tests fallback when an image has zero green leaf pixels."""
        # Pure blue image (no green canopy)
        img = Image.new("RGB", (224, 224), color=(0, 0, 255))
        pct, grade = diagnosis_service.quantify_lesion_severity(img)
        assert pct == 28.4
        assert grade == SeverityGrade.MODERATE

    def test_invalid_base64_rejection(self):
        """Verifies rejection of invalid or malformed image base64 strings."""
        with pytest.raises(ValueError, match="Invalid base64 encoding"):
            diagnosis_service.decode_and_validate_image("not_a_valid_base64_string!!!")

    def test_empty_image_payload_rejection(self):
        """Verifies rejection of empty or None image payload."""
        with pytest.raises(ValueError, match="must be a non-empty base64 string"):
            diagnosis_service.decode_and_validate_image("")

    def test_corrupt_image_bytes_rejection(self):
        """Verifies rejection of valid base64 that does not represent an image."""
        raw_non_image = b"Hello, this is just plain text, not an image format."
        b64 = base64.b64encode(raw_non_image).decode("utf-8")
        with pytest.raises(ValueError, match="Corrupt or unreadable image stream"):
            diagnosis_service.decode_and_validate_image(b64)

    def test_oversized_image_rejection(self, monkeypatch):
        """Verifies that an image payload exceeding MAX_IMAGE_SIZE_MB is rejected."""
        from app.config import settings
        # Set threshold to 1 KB for testing
        monkeypatch.setattr(settings, "MAX_IMAGE_SIZE_MB", 0.001)

        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        import io
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        with pytest.raises(ValueError, match="exceeds maximum allowable threshold"):
            diagnosis_service.decode_and_validate_image(b64)

    @pytest.mark.parametrize(
        "crop_name,severity_pct,expected_id",
        [
            ("Potato", 25.0, "POTATO_EARLY_BLIGHT"),
            ("Potato", 0.0, "POTATO_HEALTHY"),
            ("Potato Late Blight", 30.0, "POTATO_LATE_BLIGHT"),
            ("Corn", 0.0, "CORN_HEALTHY"),
            ("Corn Rust", 20.0, "CORN_COMMON_RUST"),
            ("Corn Northern", 25.0, "CORN_NORTHERN_BLIGHT"),
            ("Apple", 0.0, "APPLE_HEALTHY"),
            ("Apple", 15.0, "APPLE_SCAB"),
            ("Grape", 0.0, "GRAPE_HEALTHY"),
            ("Grape", 18.0, "GRAPE_BLACK_ROT"),
            ("Rice", 0.0, "RICE_HEALTHY"),
            ("Rice Sheath Blight", 22.0, "RICE_SHEATH_BLIGHT"),
            ("Rice Brown Spot", 18.0, "RICE_BROWN_SPOT"),
            ("Rice Bacterial Blight", 25.0, "RICE_BACTERIAL_BLIGHT"),
            ("Rice Tungro", 30.0, "RICE_TUNGRO"),
            ("Rice Blast", 15.0, "RICE_BLAST"),
            ("Bell Pepper", 0.0, "BELL_PEPPER_HEALTHY"),
            ("Bell Pepper", 16.0, "BELL_PEPPER_BACTERIAL_SPOT"),
            ("Cotton", 0.0, "COTTON_HEALTHY"),
            ("Cotton Curl Virus", 24.0, "COTTON_CURL_VIRUS"),
            ("Cotton Fusarium Wilt", 32.0, "COTTON_FUSARIUM_WILT"),
            ("Cotton", 20.0, "COTTON_BACTERIAL_BLIGHT"),
            ("Tomato Bacterial Spot", 20.0, "TOMATO_BACTERIAL_SPOT"),
            ("Tomato Late Blight", 35.0, "TOMATO_LATE_BLIGHT"),
            ("Tomato", 0.0, "TOMATO_HEALTHY"),
            ("Tomato", 28.4, "TOMATO_EARLY_BLIGHT"),
        ],
    )
    def test_multi_crop_classification(self, crop_name, severity_pct, expected_id):
        """Verifies disease classification across multi-crop catalog and healthy states."""
        pathology, conf = diagnosis_service.classify_crop_pathology(
            crop_name, severity_pct=severity_pct
        )
        assert pathology.disease_id == expected_id
        assert conf >= 0.70

    def test_catalog_and_label_mapping_integrity(self):
        """Verifies every vision label maps to a valid DISEASE_CATALOG entry and CIBRC medicines."""
        from app.services.agronomic_database import MEDICINES_CATALOG

        for label, catalog_key in diagnosis_service.PLANTVILLAGE_TO_CATALOG.items():
            assert catalog_key in DISEASE_CATALOG, f"Unmapped key {catalog_key} for {label}"

        for disease_id, pathology in DISEASE_CATALOG.items():
            for med_id in pathology.chemical_medicine_ids + pathology.organic_medicine_ids:
                assert med_id in MEDICINES_CATALOG, f"Missing medicine {med_id} in {disease_id}"
            if "healthy" in pathology.common_name.lower():
                assert len(pathology.chemical_medicine_ids) == 0

    def test_onnx_model_and_crop_hint_aliases(self):
        """Verifies trained 48-class ONNX model loads, fits <25MB, and handles crop hints."""
        assert diagnosis_service.ONNX_MODEL_PATH.exists()
        assert diagnosis_service.ONNX_MODEL_PATH.stat().st_size < 25 * 1024 * 1024
        assert len(diagnosis_service._class_labels) == 48

        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        for hint, expected_crop in [("all", None), ("Paddy", CropType.RICE), ("Pepper", CropType.BELL_PEPPER)]:
            res = diagnosis_service.predict_with_onnx(img, crop_hint=hint)
            assert res is not None
            pathology, conf = res
            assert 0.0 <= conf <= 1.0
            if expected_crop is not None:
                assert pathology.crop == expected_crop
