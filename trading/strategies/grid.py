"""
Grid Trading Strategy — multi-account aware.
"""
import logging
from utils import exchange, database, notifier

logger = logging.getLogger(__name__)


def init_grid(ex, config, account_id=1):
    symbol = config["symbol"]
    lower = config["lower_price"]
    upper = config["upper_price"]
    n = config["grid_count"]
    order_usdt = config["order_size_usdt"]

    step = (upper - lower) / n
    levels = [lower + i * step for i in range(n + 1)]

    current_price = exchange.get_ticker_price(ex, symbol)
    logger.info(f"[acct:{account_id}][{symbol}] Price: ${current_price:,.2f}, Grid: {n} levels ${lower:,.0f}-${upper:,.0f} (step ${step:,.0f})")

    if current_price < lower or current_price > upper:
        logger.warning(f"[acct:{account_id}][{symbol}] Price OUTSIDE grid range!")
        return []

    existing = database.get_active_grid_orders(symbol, account_id)
    if existing:
        logger.info(f"[acct:{account_id}][{symbol}] {len(existing)} existing orders, skipping init")
        return existing

    placed = []
    for i, level_price in enumerate(levels):
        if level_price < current_price:
            amount = order_usdt / level_price
            try:
                order = exchange.place_buy_order(ex, symbol, amount, level_price)
                order_id = order["id"]
                database.log_grid_order(order_id, symbol, "buy", i, level_price, amount, "open",
                                       account_id=account_id)
                placed.append(order_id)
                logger.info(f"[acct:{account_id}][{symbol}] BUY @ ${level_price:,.2f} (level {i})")
            except Exception as e:
                logger.error(f"[acct:{account_id}][{symbol}] Failed buy @ {level_price}: {e}")

    notifier.send_telegram(
        f"🎯 <b>Grid Init (acct:{account_id})</b>\n"
        f"{symbol}: {len(placed)} buys placed\n"
        f"Range: ${lower:,.0f}-${upper:,.0f}"
    )
    return placed


def check_and_replace(ex, config, account_id=1):
    symbol = config["symbol"]
    lower = config["lower_price"]
    upper = config["upper_price"]
    n = config["grid_count"]
    step = (upper - lower) / n
    order_usdt = config["order_size_usdt"]

    open_orders = exchange.get_open_orders(ex, symbol)
    open_ids = {o["id"] for o in open_orders}

    tracked = database.get_active_grid_orders(symbol, account_id)

    for order_id, side, level, price, amount in tracked:
        if order_id not in open_ids:
            try:
                order = ex.fetch_order(order_id, symbol)
                status = order["status"]

                if status == "closed":
                    database.update_grid_order_status(order_id, "filled")
                    database.log_trade(order_id, symbol, side, amount, price,
                                      amount * price, "filled", "grid", account_id)
                    notifier.notify_trade(symbol, side, amount, price, f"Grid(acct:{account_id})")
                    logger.info(f"[acct:{account_id}][{symbol}] FILLED: {side} @ ${price:,.2f}")

                    if side == "buy":
                        sell_price = lower + (level + 1) * step
                        if sell_price <= upper:
                            try:
                                new = exchange.place_sell_order(ex, symbol, amount, sell_price)
                                database.log_grid_order(new["id"], symbol, "sell",
                                                       level + 1, sell_price, amount, "open",
                                                       order_id, account_id)
                                logger.info(f"[acct:{account_id}][{symbol}] NEW SELL @ ${sell_price:,.2f}")
                            except Exception as e:
                                logger.error(f"Failed paired sell: {e}")
                    else:
                        buy_price = lower + (level - 1) * step
                        if buy_price >= lower:
                            try:
                                buy_amount = order_usdt / buy_price
                                new = exchange.place_buy_order(ex, symbol, buy_amount, buy_price)
                                database.log_grid_order(new["id"], symbol, "buy",
                                                       level - 1, buy_price, buy_amount, "open",
                                                       order_id, account_id)
                                logger.info(f"[acct:{account_id}][{symbol}] NEW BUY @ ${buy_price:,.2f}")
                            except Exception as e:
                                logger.error(f"Failed paired buy: {e}")
                elif status == "canceled":
                    database.update_grid_order_status(order_id, "canceled")
            except Exception as e:
                logger.error(f"Error checking order {order_id}: {e}")


def check_stop_loss(ex, config, account_id=1):
    symbol = config["symbol"]
    stop = config.get("stop_loss_price")
    if not stop:
        return False

    price = exchange.get_ticker_price(ex, symbol)
    if price < stop:
        logger.warning(f"[acct:{account_id}][{symbol}] STOP LOSS @ ${price:,.2f} < ${stop:,.2f}")
        open_orders = exchange.get_open_orders(ex, symbol)
        for o in open_orders:
            try:
                exchange.cancel_order(ex, o["id"], symbol)
                database.update_grid_order_status(o["id"], "canceled")
            except Exception as e:
                logger.error(f"Cancel failed: {e}")
        notifier.send_telegram(f"🛑 <b>STOP LOSS (acct:{account_id})</b>\n{symbol} @ ${price:,.2f}")
        return True
    return False


def run_grid(ex, config, account_id=1):
    if not config.get("enabled", True):
        return
    try:
        if check_stop_loss(ex, config, account_id):
            return
        check_and_replace(ex, config, account_id)
    except Exception as e:
        logger.error(f"Grid error acct:{account_id} {config['symbol']}: {e}", exc_info=True)
        notifier.notify_error(f"Grid acct:{account_id} {config['symbol']}: {e}")
