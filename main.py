"""
CoinGecko API Data Validation and Logging Tool

Features:
- CLI argument support for coins and currency
- Retry logic for API calls
- Validation using jsonschema
- Logs and reports in PST
- Type hints and improved error handling
- Configuration management
- Enhanced logging
"""

import json
import logging
import os
import argparse
import pytz
from datetime import datetime
from time import sleep
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

import requests
from jsonschema import validate, ValidationError
import yaml

# Setup PST timezone
PST = pytz.timezone('US/Pacific')


# Configuration dataclass
@dataclass
class Config:
    """Configuration settings for the application."""
    base_url: str = "https://api.coingecko.com/api/v3/simple/price"
    default_coins: List[str] = None
    default_currency: str = "usd"
    max_retries: int = 3
    retry_delay: int = 2
    request_timeout: int = 10
    log_level: str = "INFO"
    logs_dir: str = "logs"

    def __post_init__(self):
        if self.default_coins is None:
            self.default_coins = ["bitcoin", "ethereum"]


def load_config(config_path: str = "config.yaml") -> Config:
    """Load configuration from YAML file or use defaults."""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
                return Config(**config_data)
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}. Using defaults.")
    return Config()


def setup_logging(config: Config) -> None:
    """Setup logging configuration."""
    os.makedirs(config.logs_dir, exist_ok=True)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # Setup file handler
    file_handler = logging.FileHandler(
        os.path.join(config.logs_dir, 'api_validation.log')
    )
    file_handler.setFormatter(file_formatter)

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Setup logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.log_level.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def generate_schema(coins_list: List[str], currency: str) -> Dict[str, Any]:
    """
    Dynamically generate a JSON schema based on the coins requested.

    Args:
        coins_list: List of coin IDs to validate
        currency: Currency code for validation

    Returns:
        JSON schema dictionary
    """
    properties = {}
    for coin in coins_list:
        properties[coin] = {
            'type': 'object',
            'properties': {
                currency: {'type': 'number'},
                f'{currency}_24h_change': {'type': 'number'}
            },
            'required': [currency]
        }

    schema = {
        'type': 'object',
        'properties': properties,
        'required': coins_list
    }
    return schema


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def fetch_crypto_data(
        coins: str,
        currency: str,
        config: Config
) -> Optional[Dict[str, Any]]:
    """
    Fetch crypto data from CoinGecko with retry logic.

    Args:
        coins: Comma-separated string of coin IDs
        currency: Currency code for price comparison
        config: Configuration object

    Returns:
        JSON response data or None if failed

    Raises:
        APIError: If all retry attempts fail
    """
    params = {
        'ids': coins,
        'vs_currencies': currency,
        'include_24hr_change': 'true'
    }

    logger = logging.getLogger(__name__)

    for attempt in range(1, config.max_retries + 1):
        try:
            logger.info(f"Fetching data (attempt {attempt}/{config.max_retries})")
            response = requests.get(
                config.base_url,
                params=params,
                timeout=config.request_timeout
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Data fetched successfully: {len(data)} coins")
            return data

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt < config.max_retries:
                logger.info(f"Retrying in {config.retry_delay} seconds...")
                sleep(config.retry_delay)
            else:
                error_msg = f"All {config.max_retries} retry attempts failed"
                logger.error(error_msg)
                raise APIError(error_msg) from e
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise APIError(f"Invalid JSON response: {e}") from e

    return None


def validate_crypto_data(
        data: Optional[Dict[str, Any]],
        coins_list: List[str],
        currency: str
) -> Dict[str, Any]:
    """
    Validate fetched crypto data and include prices with 24h change in report.

    Args:
        data: API response data
        coins_list: List of expected coin IDs
        currency: Currency code for validation

    Returns:
        Validation report dictionary
    """
    now_pst = datetime.now(PST).isoformat()
    report = {
        'timestamp': now_pst,
        'status': 'PASS',
        'details': [],
        'coins_requested': coins_list,
        'currency': currency,
        'summary': {}
    }

    logger = logging.getLogger(__name__)

    if not data:
        report['status'] = 'FAIL'
        report['details'].append('No data received from API.')
        logger.error("Validation failed: No data received")
        return report

    # Schema validation
    try:
        schema = generate_schema(coins_list, currency)
        validate(instance=data, schema=schema)
        report['details'].append('Schema validation passed.')
        logger.info("Schema validation passed")
    except ValidationError as e:
        report['status'] = 'FAIL'
        report['details'].append(f'Schema validation error: {e.message}')
        logger.error(f"Schema validation failed: {e.message}")

    # Data validation
    valid_coins = 0
    total_coins = len(coins_list)

    for coin in coins_list:
        if coin not in data:
            report['status'] = 'FAIL'
            report['details'].append(f'Missing data for {coin}')
            logger.warning(f"Missing data for {coin}")
            continue

        coin_data = data[coin]
        price = coin_data.get(currency)
        pct_change_key = f"{currency}_24h_change"
        pct_change = coin_data.get(pct_change_key)

        # Validate price
        if price is None or not isinstance(price, (int, float)) or price <= 0:
            report['status'] = 'FAIL'
            report['details'].append(f'Invalid or missing price for {coin}: {price}')
            logger.error(f"Invalid price for {coin}: {price}")
            continue

        # Validate % change (optional field)
        if pct_change is not None and not isinstance(pct_change, (int, float)):
            report['status'] = 'FAIL'
            report['details'].append(f'Invalid 24h % change for {coin}: {pct_change}')
            logger.error(f"Invalid 24h change for {coin}: {pct_change}")
            continue

        # Add to summary
        report['summary'][coin] = {
            'price': price,
            'currency': currency.upper(),
            '24h_change': pct_change
        }

        change_str = f" (24h change: {pct_change:+.2f}%)" if pct_change is not None else ""
        report['details'].append(
            f'✓ {coin}: {price:.2f} {currency.upper()}{change_str}'
        )
        valid_coins += 1

    # Final status
    if report['status'] == 'PASS' and valid_coins == total_coins:
        report['details'].append(f'✓ All {total_coins} coins validated successfully.')
        logger.info(f"All {total_coins} coins validated successfully")
    else:
        report['status'] = 'FAIL'
        report['details'].append(f'✗ Only {valid_coins}/{total_coins} coins validated successfully.')
        logger.error(f"Only {valid_coins}/{total_coins} coins validated successfully")

    return report


def save_report(report: Dict[str, Any], config: Config) -> str:
    """
    Save validation report to JSON file with PST timestamp.

    Args:
        report: Validation report dictionary
        config: Configuration object

    Returns:
        Path to saved report file
    """
    timestamp = datetime.now(PST).strftime('%Y%m%d_%H%M%S')
    filename = f'api_validation_report_{timestamp}.json'
    filepath = os.path.join(config.logs_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(report, file, indent=4, ensure_ascii=False)

        logger = logging.getLogger(__name__)
        logger.info(f'Report saved to {filepath}')
        return filepath

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to save report: {e}')
        raise


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for flexibility."""
    parser = argparse.ArgumentParser(
        description='CoinGecko API Data Validation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --coins bitcoin,ethereum --currency usd
  python main.py --coins solana,dogecoin --currency eur
  python main.py --config custom_config.yaml
        """
    )

    parser.add_argument(
        '--coins',
        default='bitcoin,ethereum',
        help='Comma-separated list of coins to fetch (default: bitcoin,ethereum)'
    )

    parser.add_argument(
        '--currency',
        default='usd',
        help='Currency for price comparison (default: usd)'
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--output-format',
        choices=['json', 'summary'],
        default='json',
        help='Output format (default: json)'
    )

    return parser.parse_args()


def print_summary(report: Dict[str, Any]) -> None:
    """Print a human-readable summary of the validation report."""
    print(f"\n{'=' * 50}")
    print(f"CoinGecko API Validation Report")
    print(f"{'=' * 50}")
    print(f"Status: {report['status']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Currency: {report['currency'].upper()}")
    print(f"Coins Requested: {', '.join(report['coins_requested'])}")
    print(f"\nResults:")

    if report['summary']:
        for coin, data in report['summary'].items():
            change = data['24h_change']
            change_str = f" ({change:+.2f}%)" if change is not None else ""
            print(f"  {coin}: {data['price']:.2f} {data['currency']}{change_str}")

    print(f"\nDetails:")
    for detail in report['details']:
        print(f"  {detail}")
    print(f"{'=' * 50}\n")


def main() -> None:
    """Main workflow for fetching, validating, and saving crypto data."""
    args = parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override config with CLI args if provided
    if args.verbose:
        config.log_level = "DEBUG"

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    try:
        logger.info('Starting API data validation workflow')

        # Parse coins list
        coins_list = [coin.strip() for coin in args.coins.split(',')]
        logger.info(f"Validating coins: {coins_list}")

        # Fetch data
        data = fetch_crypto_data(args.coins, args.currency, config)

        # Validate data
        report = validate_crypto_data(data, coins_list, args.currency)

        # Save report
        filepath = save_report(report, config)

        # Output results
        if args.output_format == 'summary':
            print_summary(report)
        else:
            print(json.dumps(report, indent=4, ensure_ascii=False))

        logger.info('API data validation workflow completed successfully')

        # Exit with appropriate code
        exit_code = 0 if report['status'] == 'PASS' else 1
        exit(exit_code)

    except APIError as e:
        logger.error(f"API Error: {e}")
        exit(1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()