"""
Telegram notification utility.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message: str):
    """Send a Telegram message. Silently skips if not configured."""
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }, timeout=10)
    except Exception as e:
        print(f"Telegram send failed: {e}")


def notify_trade(symbol, side, amount, price, strategy):
    emoji = "🟢" if side == "buy" else "🔴"
    msg = (
        f"{emoji} <b>{strategy} {side.upper()}</b>\n"
        f"{symbol}: {amount:.6f} @ ${price:,.2f}\n"
        f"Total: ${amount * price:,.2f}"
    )
    send_telegram(msg)


def notify_error(error_msg):
    send_telegram(f"⚠️ <b>Bot Error</b>\n<code>{error_msg}</code>")


def notify_startup(config_summary):
    send_telegram(f"🚀 <b>Grid Bot Started</b>\n<pre>{config_summary}</pre>")


def notify_daily_summary(stats):
    msg = (
        f"📊 <b>Daily Summary</b>\n"
        f"Grid fills: {stats.get('grid_fills', 0)}\n"
        f"DCA total: ${stats.get('dca_total_usdt', 0):.2f}\n"
        f"Total trades: {stats.get('total_trades', 0)}"
    )
    send_telegram(msg)
