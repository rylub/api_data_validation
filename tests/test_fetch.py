import requests_mock
import pytest
from main import fetch_crypto_data, Config, APIError


def test_fetch_crypto_data_success():
    """Test that fetch_crypto_data returns correct data when API call succeeds."""
    config = Config()  # Create config object
    with requests_mock.Mocker() as m:
        m.get(
            'https://api.coingecko.com/api/v3/simple/price',
            json={'bitcoin': {'usd': 30000, 'usd_24h_change': 2.5}}
        )
        data = fetch_crypto_data('bitcoin', 'usd', config)
        assert data == {'bitcoin': {'usd': 30000, 'usd_24h_change': 2.5}}


def test_fetch_crypto_data_failure():
    """Test that fetch_crypto_data raises APIError on failure."""
    config = Config(max_retries=1)  # Use config with 1 retry
    with requests_mock.Mocker() as m:
        m.get(
            'https://api.coingecko.com/api/v3/simple/price',
            status_code=500
        )
        with pytest.raises(APIError):
            fetch_crypto_data('bitcoin', 'usd', config)