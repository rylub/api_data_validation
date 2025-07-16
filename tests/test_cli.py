import pytest
from main import parse_args

def test_parse_args_defaults(monkeypatch):
    """Test CLI defaults are returned when no args provided."""
    monkeypatch.setattr('sys.argv', ['main.py'])
    args = parse_args()
    assert args.coins == 'bitcoin,ethereum'
    assert args.currency == 'usd'
    assert args.config == 'config.yaml'  # New default
    assert args.verbose is False  # New default
    assert args.output_format == 'json'  # New default

def test_parse_args_custom(monkeypatch):
    """Test CLI returns provided arguments correctly."""
    monkeypatch.setattr('sys.argv', ['main.py', '--coins', 'solana', '--currency', 'eur'])
    args = parse_args()
    assert args.coins == 'solana'
    assert args.currency == 'eur'

def test_parse_args_new_options(monkeypatch):
    """Test new CLI options work correctly."""
    monkeypatch.setattr('sys.argv', [
        'main.py',
        '--coins', 'bitcoin',
        '--currency', 'usd',
        '--verbose',
        '--output-format', 'summary'
    ])
    args = parse_args()
    assert args.coins == 'bitcoin'
    assert args.currency == 'usd'
    assert args.verbose is True
    assert args.output_format == 'summary'