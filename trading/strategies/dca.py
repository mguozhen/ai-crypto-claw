"""
DCA (Dollar Cost Averaging) Strategy — multi-account aware.
"""
import logging
from datetime import datetime, timedelta
from utils import exchange, database, notifier

logger = logging.getLogger(__name__)


def should_buy(symbol, interval_hours, buy_on_dip_only, dip_threshold_pct, current_price, account_id=1):
    last_time_str = database.get_last_dca_time(symbol, account_id)
    if last_time_str is None:
        return True

    last_time = datetime.fromisoformat(last_time_str)
    if datetime.now() - last_time < timedelta(hours=interval_hours):
        return False

    if buy_on_dip_only:
        last_price = database.get_last_dca_price(symbol, account_id)
        if last_price and current_price > last_price * (1 - dip_threshold_pct / 100):
            logger.info(f"[DCA acct:{account_id}][{symbol}] Skipping: not below dip threshold")
            return False

    return True


def execute_dca(ex, position, global_config, account_id=1):
    symbol = position["symbol"]
    amount_usdt = position["amount_usdt"]
    interval_hours = position["interval_hours"]
    buy_on_dip_only = global_config.get("buy_on_dip_only", False)
    dip_pct = global_config.get("dip_threshold_pct", 0)

    try:
        current_price = exchange.get_ticker_price(ex, symbol)

        if not should_buy(symbol, interval_hours, buy_on_dip_only, dip_pct, current_price, account_id):
            return

        amount_crypto = amount_usdt / current_price
        logger.info(f"[DCA acct:{account_id}][{symbol}] Buying ${amount_usdt} @ ${current_price:,.2f}")

        order = exchange.place_buy_order(ex, symbol, amount_crypto)
        order_id = order.get("id", f"dca-{datetime.now().timestamp()}")

        database.log_dca(symbol, amount_usdt, amount_crypto, current_price, account_id)
        database.log_trade(order_id, symbol, "buy", amount_crypto, current_price,
                          amount_usdt, "filled", "dca", account_id)
        notifier.notify_trade(symbol, "buy", amount_crypto, current_price, f"DCA(acct:{account_id})")
    except Exception as e:
        logger.error(f"DCA error acct:{account_id} {symbol}: {e}", exc_info=True)
        notifier.notify_error(f"DCA acct:{account_id} {symbol}: {e}")


def run_dca(ex, config, account_id=1):
    if not config.get("enabled", True):
        return
    for position in config["positions"]:
        execute_dca(ex, position, config, account_id)
