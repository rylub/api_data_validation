# CoinGecko API Data Validation Tool

This Python tool fetches cryptocurrency prices from the CoinGecko API, validates the response using dynamically generated JSON schemas, and logs structured reports with PST timestamps. It includes a command-line interface, retry logic, and automated testing, demonstrating practical QA, API integration, and test-driven development workflows.

## Features

- Fetches real-time crypto price data with retry logic on failures
- Dynamic JSON schema validation for arbitrary coin sets
- Command-line interface for specifying coins and currency
- Structured logging with PST timestamps for clear traceability
- Automated tests using pytest for validation and fetch logic
- Modular and clear code structure for easy extension

## Project Structure

```
api_data_validation/
├── logs/                   # Stores API call logs and validation reports
├── tests/                  # Unit tests for CLI, fetch, and validation
│   ├── test_cli.py
│   ├── test_fetch.py
│   └── test_validate.py
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
└── README.md               # Project overview
```

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/api_data_validation.git
cd api_data_validation
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run from the command line with default coins (bitcoin, ethereum) and USD:

```bash
python main.py
```

Specify custom coins and currency:

```bash
python main.py --coins solana,dogecoin --currency eur
```

## Testing

Run automated tests with:

```bash
pytest
```

Ensure all tests pass before deploying or pushing changes.

## Why This Project

This project showcases API integration, data validation, structured logging, and test-driven workflows, demonstrating readiness for QA, automation, and Python development roles.

## Contact

Created by Ryan Lubell  
Email: lubellryan@gmail.com
