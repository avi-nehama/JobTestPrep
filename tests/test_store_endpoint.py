import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app


def test_store_rejects_empty_payload():
    client = TestClient(app)
    # Patch the storage backend to ensure it is not called
    with patch('src.main.payload_storage.store', new=AsyncMock()) as mock_store:
        response = client.post('/store', json={})
        assert response.status_code == 400
        body = response.json()
        assert isinstance(body, dict)
        assert 'detail' in body
        assert 'Empty JSON body' in body['detail']
        mock_store.assert_not_called()
