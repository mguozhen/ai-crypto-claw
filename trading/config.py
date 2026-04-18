"""
Crypto Grid Bot — Configuration

Global defaults + per-user config support.
"""
import json
from utils import database

# ============ Default Strategy (used when user has no custom config) ============

DEFAULT_CONFIG = {
    "btc_grid": {
        "symbol": "BTC/USDT",
        "enabled": True,
        "lower_price": 62000,
        "upper_price": 90000,
        "grid_count": 10,
        "total_investment": 500,
        "order_size_usdt": 50,
        "max_open_orders": 10,
        "stop_loss_price": 55000,
        "take_profit_price": None,
    },
    "eth_grid": {
        "symbol": "ETH/USDT",
        "enabled": True,
        "lower_price": 1800,
        "upper_price": 3000,
        "grid_count": 10,
        "total_investment": 300,
        "order_size_usdt": 30,
        "max_open_orders": 10,
        "stop_loss_price": 1600,
        "take_profit_price": None,
    },
    "dca": {
        "enabled": True,
        "positions": [
            {"symbol": "BTC/USDT", "amount_usdt": 10, "interval_hours": 24},
            {"symbol": "ETH/USDT", "amount_usdt": 6, "interval_hours": 24},
        ],
        "buy_on_dip_only": False,
        "dip_threshold_pct": 0,
    },
}

# ============ Risk Management (global) ============
RISK_CONFIG = {
    "max_total_exposure_usdt": 1200,
    "daily_loss_limit_pct": 5,
    "min_usdt_reserve": 200,
}

# ============ Execution (global) ============
EXECUTION_CONFIG = {
    "check_interval_seconds": 60,
    "dca_check_interval_minutes": 60,
    "log_level": "INFO",
    "dry_run": False,
}


def get_config_for_user(user_id):
    """Load per-user config from database, fallback to DEFAULT_CONFIG."""
    user_config = database.get_user_config(user_id)
    if user_config:
        # Merge with defaults (user config may not have all keys)
        merged = json.loads(json.dumps(DEFAULT_CONFIG))
        for key in ["btc_grid", "eth_grid", "dca"]:
            if key in user_config:
                merged[key].update(user_config[key])
        return merged
    return json.loads(json.dumps(DEFAULT_CONFIG))
