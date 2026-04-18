"""
OKX (欧易) Exchange wrapper via CCXT.
Supports multiple accounts.
"""
import os
import ccxt
from dotenv import load_dotenv

load_dotenv()


def get_exchange():
    """Returns an authenticated CCXT OKX client for the main account (.env)."""
    api_key = os.getenv("OKX_API_KEY")
    secret = os.getenv("OKX_SECRET_KEY")
    passphrase = os.getenv("OKX_PASSPHRASE")
    demo_mode = os.getenv("OKX_DEMO_MODE", "1") == "1"

    if not all([api_key, secret, passphrase]):
        raise ValueError("Missing OKX credentials in .env file")

    return _create_exchange(api_key, secret, passphrase, demo_mode)


def get_exchange_for_account(api_key, secret, passphrase, demo_mode=False):
    """Returns an authenticated CCXT OKX client for a sub-account."""
    return _create_exchange(api_key, secret, passphrase, demo_mode)


def _create_exchange(api_key, secret, passphrase, demo_mode):
    exchange = ccxt.okx({
        "apiKey": api_key,
        "secret": secret,
        "password": passphrase,
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })
    if demo_mode:
        exchange.set_sandbox_mode(True)
    return exchange


def get_balance(exchange, asset="USDT"):
    balance = exchange.fetch_balance()
    return balance.get(asset, {}).get("free", 0)


def get_full_balance(exchange):
    """Get all non-zero balances."""
    balance = exchange.fetch_balance()
    result = {}
    for asset, info in balance.items():
        if isinstance(info, dict) and info.get("free", 0) > 0:
            result[asset] = {"free": info["free"], "used": info.get("used", 0), "total": info.get("total", 0)}
    return result


def get_ticker_price(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker["last"]


def place_buy_order(exchange, symbol, amount, price=None):
    if price:
        return exchange.create_limit_buy_order(symbol, amount, price)
    return exchange.create_market_buy_order(symbol, amount)


def place_sell_order(exchange, symbol, amount, price=None):
    if price:
        return exchange.create_limit_sell_order(symbol, amount, price)
    return exchange.create_market_sell_order(symbol, amount)


def cancel_order(exchange, order_id, symbol):
    return exchange.cancel_order(order_id, symbol)


def get_open_orders(exchange, symbol=None):
    return exchange.fetch_open_orders(symbol)


def get_closed_orders(exchange, symbol, since=None, limit=100):
    return exchange.fetch_closed_orders(symbol, since=since, limit=limit)
