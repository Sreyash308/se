"""
Pytest Fixtures and Global Configuration for PlantCare AI Test Suite.
"""

import base64
import io
import pytest
from PIL import Image
from starlette.testclient import TestClient

from app.main import app
from app.services.spatial_inventory_service import SpatialInventoryService


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def clean_spatial_service():
    """Provides a fresh isolated instance of SpatialInventoryService."""
    return SpatialInventoryService()


@pytest.fixture(scope="session")
def valid_leaf_image_base64():
    """Generates a small valid test JPEG image base64 string."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


@pytest.fixture(scope="session")
def lesion_leaf_image_base64():
    """Generates an image with green background and brown necrotic lesions."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    # Draw necrotic brown spot
    for x in range(80, 140):
        for y in range(80, 140):
            img.putpixel((x, y), (120, 60, 20))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64
