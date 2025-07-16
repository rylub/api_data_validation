# CoinGecko API Data Validation Tool

[![CI](https://github.com/rylub/api_data_validation/actions/workflows/python-ci.yml/badge.svg)](https://github.com/rylub/api_data_validation/actions/workflows/python-ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust Python tool for fetching cryptocurrency prices from the CoinGecko API, validating responses using dynamically generated JSON schemas, and generating comprehensive reports with PST timestamps. This project demonstrates modern Python development practices including type hints, comprehensive testing, CI/CD, and professional code organization.

## Features

- **Robust API Integration**: Fetches real-time crypto price data with intelligent retry logic
- **Dynamic Schema Validation**: Automatically generates JSON schemas for arbitrary coin sets
- **Flexible CLI Interface**: Command-line interface with extensive customization options
- **Structured Logging**: Comprehensive logging with PST timestamps and multiple output formats
- **Comprehensive Testing**: Full test suite with CI/CD pipeline
- **Configuration Management**: YAML-based configuration with environment override support
- **Type Safety**: Complete type hints throughout the codebase
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## Project Structure

```
api_data_validation/
├── .github/workflows/     # GitHub Actions CI/CD
│   └── python-ci.yml
├── tests/                 # Comprehensive test suite
│   ├── test_cli.py
│   ├── test_fetch.py
│   └── test_validate.py
├── logs/                  # API call logs and validation reports
├── main.py               # Main application entry point
├── config.yaml           # Configuration file
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml        # Modern Python project configuration
└── README.md            # This file
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rylub/api_data_validation.git
   cd api_data_validation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

**Run with default settings** (bitcoin, ethereum in USD):
```bash
python main.py
```

**Specify custom coins and currency:**
```bash
python main.py --coins solana,dogecoin --currency eur
```

**Use summary output format:**
```bash
python main.py --coins bitcoin,ethereum --currency usd --output-format summary
```

**Enable verbose logging:**
```bash
python main.py --coins bitcoin --currency usd --verbose
```

**Use custom configuration file:**
```bash
python main.py --config my_config.yaml
```

## Sample Output

### JSON Format (default)
```json
{
    "timestamp": "2025-07-16T12:36:03-07:00",
    "status": "PASS",
    "details": [
        "Schema validation passed.",
        "✓ bitcoin: 119192.00 USD (24h change: +2.08%)",
        "✓ ethereum: 3360.86 USD (24h change: +9.47%)",
        "✓ All 2 coins validated successfully."
    ],
    "coins_requested": ["bitcoin", "ethereum"],
    "currency": "usd",
    "summary": {
        "bitcoin": {
            "price": 119192,
            "currency": "USD",
            "24h_change": 2.08
        },
        "ethereum": {
            "price": 3360.86,
            "currency": "USD",
            "24h_change": 9.47
        }
    }
}
```

### Summary Format
```
==================================================
CoinGecko API Validation Report
==================================================
Status: PASS
Timestamp: 2025-07-16T12:36:03-07:00
Currency: USD
Coins Requested: bitcoin, ethereum

Results:
  bitcoin: 119192.00 USD (+2.08%)
  ethereum: 3360.86 USD (+9.47%)

Details:
  Schema validation passed.
  ✓ bitcoin: 119192.00 USD (24h change: +2.08%)
  ✓ ethereum: 3360.86 USD (24h change: +9.47%)
  ✓ All 2 coins validated successfully.
==================================================
```

## Configuration

The application uses a YAML configuration file (`config.yaml`) for default settings:

```yaml
# API Configuration
base_url: "https://api.coingecko.com/api/v3/simple/price"
request_timeout: 10
max_retries: 3
retry_delay: 2

# Default Values
default_coins:
  - "bitcoin"
  - "ethereum"
default_currency: "usd"

# Logging Configuration
log_level: "INFO"
logs_dir: "logs"
```

## Testing

Run the comprehensive test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=.
```

## CI/CD Pipeline

This project includes a GitHub Actions pipeline that:

- Tests across Python 3.9-3.11
- Validates code quality with linting
- Runs comprehensive test suite
- Performs integration tests with real API calls
- Ensures cross-platform compatibility

## Technical Highlights

- **Type Safety**: Complete type hints throughout the codebase
- **Error Handling**: Custom exceptions with detailed error messages  
- **Configuration Management**: YAML-based config with sensible defaults
- **Retry Logic**: Intelligent retry mechanism for API failures
- **Data Validation**: Dynamic JSON schema generation and validation
- **Logging**: Structured logging with configurable levels
- **Testing**: Comprehensive test coverage with mocking
- **Documentation**: Professional documentation and examples

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes and add tests
5. Run the test suite: `python -m pytest tests/ -v`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Requirements

### Production Dependencies
- `requests>=2.31.0` - HTTP library for API calls
- `jsonschema>=4.19.2` - JSON schema validation
- `pytz>=2023.3` - Timezone handling
- `PyYAML>=6.0.1` - Configuration file parsing

### Development Dependencies
- `pytest>=7.4.3` - Testing framework
- `requests-mock>=1.11.0` - HTTP request mocking for tests

## License

This project is licensed under the MIT License.

## Author

**Ryan Lubell**
- Email: lubellryan@gmail.com
- GitHub: [@rylub](https://github.com/rylub)

## Acknowledgments

- [CoinGecko API](https://coingecko.com/api) for providing cryptocurrency data
- Python community for excellent libraries and tools

## Project Status

This project demonstrates:
- Production-ready code quality
- Comprehensive testing and CI/CD
- Modern Python development practices
- Professional software engineering workflows
