"""
AI Advisor — GPT-5.4 via OpenRouter

Provides intelligent decisions for the grid bot:
1. Should we adjust grid range? (market trend changed)
2. Should we pause grid? (high volatility / crash detected)
3. Smart DCA: should we buy more on this dip?
4. Daily market briefing via Telegram
"""
import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ai_advisor")

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("AI_MODEL", "openai/gpt-5.4")
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def _call_llm(system_prompt: str, user_prompt: str, max_tokens=1000) -> str:
    """Call OpenRouter API."""
    if not API_KEY:
        logger.warning("OPENROUTER_API_KEY not set, AI advisor disabled")
        return ""

    try:
        resp = requests.post(API_URL, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/crypto-grid-bot",
            "X-Title": "Crypto Grid Bot",
        }, json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }, timeout=30)

        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        return ""


def analyze_market(btc_price, eth_price, btc_24h_change=None, eth_24h_change=None):
    """
    Analyze current market and return grid adjustment recommendations.
    Returns dict with actions.
    """
    system = """You are a crypto trading advisor for a grid bot. Your job:
1. Analyze current BTC and ETH prices and recent changes
2. Recommend whether to KEEP, ADJUST, or PAUSE the grid strategy
3. If ADJUST, recommend new grid range (lower_price, upper_price)
4. Provide a brief market outlook

Respond in JSON only:
{
    "btc_action": "KEEP|ADJUST|PAUSE",
    "btc_reason": "brief reason",
    "btc_grid": {"lower": 0, "upper": 0},
    "eth_action": "KEEP|ADJUST|PAUSE",
    "eth_reason": "brief reason",
    "eth_grid": {"lower": 0, "upper": 0},
    "market_outlook": "1-2 sentence outlook",
    "risk_level": "LOW|MEDIUM|HIGH|EXTREME"
}"""

    user = f"""Current market data ({datetime.now().strftime('%Y-%m-%d %H:%M')}):
- BTC: ${btc_price:,.2f} {f'(24h: {btc_24h_change:+.1f}%)' if btc_24h_change else ''}
- ETH: ${eth_price:,.2f} {f'(24h: {eth_24h_change:+.1f}%)' if eth_24h_change else ''}

Current grid settings:
- BTC grid: $62,000 - $90,000 (10 levels)
- ETH grid: $1,800 - $3,000 (10 levels)

Analyze and recommend grid adjustments."""

    result = _call_llm(system, user)
    if not result:
        return None

    try:
        # Strip markdown code blocks if present
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1]
            clean = clean.rsplit("```", 1)[0]
        return json.loads(clean)
    except (json.JSONDecodeError, IndexError):
        logger.error(f"Failed to parse AI response: {result[:200]}")
        return None


def should_emergency_pause(btc_price, eth_price, btc_prev_price, eth_prev_price):
    """Quick check: should we emergency pause? (>10% drop in short period)"""
    if btc_prev_price and btc_price < btc_prev_price * 0.90:
        return True, f"BTC crashed {((btc_price/btc_prev_price)-1)*100:.1f}%"
    if eth_prev_price and eth_price < eth_prev_price * 0.85:
        return True, f"ETH crashed {((eth_price/eth_prev_price)-1)*100:.1f}%"
    return False, ""


def generate_daily_briefing(btc_price, eth_price, portfolio_value, trade_count, grid_fills):
    """Generate a daily market briefing for Telegram."""
    system = """You are a crypto trading bot assistant. Generate a concise daily briefing in Chinese.
Include: market status, portfolio performance, and one actionable suggestion.
Keep it under 200 characters. Use emoji sparingly."""

    user = f"""Daily data:
- BTC: ${btc_price:,.0f}
- ETH: ${eth_price:,.0f}
- Portfolio: ${portfolio_value:,.2f}
- Trades today: {trade_count}
- Grid fills: {grid_fills}
- Date: {datetime.now().strftime('%Y-%m-%d')}"""

    return _call_llm(system, user, max_tokens=300)


def evaluate_dca_timing(symbol, current_price, avg_buy_price, market_sentiment=None):
    """Should we DCA now or wait for a better price?"""
    system = """You are a DCA advisor. Given the current price vs average buy price,
recommend: BUY_NOW, WAIT, or BUY_DOUBLE (buy 2x the normal amount on a dip).
Respond in JSON: {"action": "BUY_NOW|WAIT|BUY_DOUBLE", "reason": "brief"}"""

    user = f"""{symbol}:
- Current: ${current_price:,.2f}
- Avg buy: ${avg_buy_price:,.2f} {f'({((current_price/avg_buy_price)-1)*100:+.1f}% vs avg)' if avg_buy_price else ''}
- Sentiment: {market_sentiment or 'unknown'}"""

    result = _call_llm(system, user, max_tokens=200)
    if not result:
        return {"action": "BUY_NOW", "reason": "AI unavailable, defaulting to DCA schedule"}

    try:
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    except (json.JSONDecodeError, IndexError):
        return {"action": "BUY_NOW", "reason": "Parse error, defaulting to schedule"}
