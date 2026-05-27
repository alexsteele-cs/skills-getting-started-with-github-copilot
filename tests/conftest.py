from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client():
    """Provide a fresh TestClient for each test."""
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Restore in-memory activities after each test to avoid cross-test pollution."""
    original = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)
