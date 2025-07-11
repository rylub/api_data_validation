import pytest
import requests_mock
from main import fetch_crypto_data

def test_fetch_crypto_data_success():
    """Test that fetch_crypto_data returns correct data when API call succeeds."""
    with requests_mock.Mocker() as m:
        m.get(
            'https://api.coingecko.com/api/v3/simple/price',
            json={'bitcoin': {'usd': 30000}}
        )
        data = fetch_crypto_data('bitcoin', 'usd')
        assert data is not None
        assert 'bitcoin' in data
        assert 'usd' in data['bitcoin']
        assert isinstance(data['bitcoin']['usd'], (int, float))

def test_fetch_crypto_data_failure(monkeypatch):
    """Test that fetch_crypto_data returns None on failure."""
    def mock_get(*args, **kwargs):
        raise requests_mock.exceptions.NoMockAddress

    monkeypatch.setattr('requests.get', mock_get)
    data = fetch_crypto_data('bitcoin', 'usd', retries=1)
    assert data is None