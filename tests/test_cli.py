import pytest
from main import parse_args

def test_parse_args_defaults(monkeypatch):
    """Test CLI defaults are returned when no args provided."""
    monkeypatch.setattr('sys.argv', ['main.py'])
    args = parse_args()
    assert args.coins == 'bitcoin,ethereum'
    assert args.currency == 'usd'

def test_parse_args_custom(monkeypatch):
    """Test CLI returns provided arguments correctly."""
    monkeypatch.setattr('sys.argv', ['main.py', '--coins', 'solana', '--currency', 'eur'])
    args = parse_args()
    assert args.coins == 'solana'
    assert args.currency == 'eur'
