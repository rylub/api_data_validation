"""
CoinGecko API Data Validation and Logging Tool

Features:
- CLI argument support for coins and currency
- Retry logic for API calls
- Validation using jsonschema
- Logs and reports in PST
- Comments for clarity
"""

import requests, json, logging, os, argparse, pytz
from time import sleep
from datetime import datetime
from jsonschema import validate, ValidationError

# Setup PST timezone
pst = pytz.timezone('US/Pacific')

# Setup Logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/api_validation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# JSON schema for validation
def generate_schema(coins_list):
    #Dyanmically generate a json schema based on the coins requested
    properties = {}
    for coin in coins_list:
        properties[coin] = {
            'type': 'object',
            'properties': {
                'usd': {'type': 'number'}
            },
            'required': ['usd']
        }
    schema = {
        'type': 'object',
        'properties': properties,
        'required': coins_list
    }
    return schema

def fetch_crypto_data(coins: str, currency: str, retries: int = 3):
    """Fetch crypto data from CoinGecko with retry logic."""
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': coins,
        'vs_currencies': currency,
        'include_24hr_change': 'true'  # ✅ include 24h change
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            logging.info('Data fetched successfully.')
            return response.json()
        except Exception as e:
            logging.warning(f'Attempt {attempt} failed: {e}')
            if attempt < retries:
                sleep(2)
                return None
            else:
                logging.error('All retry attempts failed.')
                return None
    return None

def validate_crypto_data(data, coins_list, currency):
    """Validate fetched crypto data and include prices with 24h change in report."""
    now_pst = datetime.now(pst).isoformat()
    report = {'timestamp': now_pst, 'status': 'PASS', 'details': []}
    if not data:
        report['status'] = 'FAIL'
        report['details'].append('No data received from API.')
        return report

    try:
        schema = generate_schema(coins_list)
        validate(instance=data, schema=schema)
        report['details'].append('Schema validation passed.')
    except ValidationError as e:
        report['status'] = 'FAIL'
        report['details'].append(f'Schema validation error: {e.message}')

    for coin, details in data.items():
        price = details.get(currency)
        pct_change_key = f"{currency}_24h_change"
        pct_change = details.get(pct_change_key)

        # Validate price
        if price is None or not isinstance(price, (int, float)) or price <= 0:
            report['status'] = 'FAIL'
            report['details'].append(f'Invalid or missing price for {coin}: {price}')
        # Validate % change
        elif pct_change is None or not isinstance(pct_change, (int, float)):
            report['status'] = 'FAIL'
            report['details'].append(f'Invalid or missing 24h % change for {coin}: {pct_change}')
        else:
            report['details'].append(
                f'Price for {coin}: {price:.2f} {currency.upper()} (24h change: {pct_change:+.2f}%)'
            )

    if report['status'] == "PASS":
        report['details'].append('All checks passed.')
    return report


def save_report(report):
    """Save validation report to JSON file with PST timestamp."""
    timestamp = datetime.now(pst).strftime('%Y%m%d_%H%M%S')
    path = f'logs/api_validation_report_{timestamp}.json'
    with open(path, 'w') as file:
        json.dump(report, file, indent=4)
    logging.info(f'Report saved to {path}')

def parse_args():
    """Parse CLI arguments for flexibility."""
    parser = argparse.ArgumentParser(description='CoinGecko API Data Validation Tool')
    parser.add_argument('--coins', default='bitcoin,ethereum', help='Comma-separated list of coins to fetch.')
    parser.add_argument('--currency', default='usd', help='Currency for price comparison.')
    return parser.parse_args()

def main():
    """Main workflow for fetching, validating, and saving crypto data."""
    args = parse_args()
    logging.info('Starting API data validation workflow.')
    data = fetch_crypto_data(args.coins, args.currency)
    coins_list = [coin.strip() for coin in args.coins.split(',')]
    report = validate_crypto_data(data, coins_list, args.currency)  # ✅ Pass currency
    save_report(report)
    print(json.dumps(report, indent=4))
    logging.info('API data validation workflow completed.')

if __name__ == '__main__':
    main()

