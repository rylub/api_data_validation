import pytest
from main import validate_crypto_data

def test_validate_crypto_data_valid():
    """Test validation passes with correct data."""
    data = {
        'bitcoin': {'usd': 20000, 'usd_24h_change': 1.5},
        'ethereum': {'usd': 1500, 'usd_24h_change': -0.5}
    }
    coins_list = ['bitcoin', 'ethereum']
    report = validate_crypto_data(data, coins_list, 'usd')
    assert report['status'] == 'PASS'
    assert any('Schema validation passed.' in detail for detail in report['details'])
    assert any('All checks passed.' in detail for detail in report['details'])

def test_validate_crypto_data_invalid():
    """Test validation fails with incorrect data (negative price)."""
    data = {'bitcoin': {'usd': -1000, 'usd_24h_change': 0.5}}
    coins_list = ['bitcoin']
    report = validate_crypto_data(data, coins_list, 'usd')
    assert report['status'] == 'FAIL'
    assert any('Invalid or missing price' in detail for detail in report['details'])

def test_validate_crypto_data_missing():
    """Test validation fails when no data is provided."""
    report = validate_crypto_data(None, ['bitcoin'], 'usd')
    assert report['status'] == 'FAIL'
    assert any('No data received from API' in detail for detail in report['details'])
