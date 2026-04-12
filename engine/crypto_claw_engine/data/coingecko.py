import httpx

from crypto_claw_engine.data.base import PriceSnapshot
from crypto_claw_engine.errors import DataGap

SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOGE": "dogecoin",
    "LINK": "chainlink",
    "DOT": "polkadot",
}


class CoinGeckoAdapter:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, client: httpx.Client | None = None, timeout: float = 10.0):
        self._client = client or httpx.Client(base_url=self.BASE_URL, timeout=timeout)

    def get_price(self, symbol: str) -> PriceSnapshot:
        coin_id = SYMBOL_TO_ID.get(symbol.upper())
        if not coin_id:
            raise DataGap("coingecko", symbol, "unknown symbol")
        try:
            r = self._client.get(
                "/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                },
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("coingecko", symbol, f"http error: {e}") from e

        data = r.json().get(coin_id)
        if not data or "usd" not in data:
            raise DataGap("coingecko", symbol, "no price in response")

        return PriceSnapshot(
            symbol=symbol.upper(),
            price_usd=float(data["usd"]),
            market_cap_usd=data.get("usd_market_cap"),
            volume_24h_usd=data.get("usd_24h_vol"),
        )
