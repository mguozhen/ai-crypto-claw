from datetime import datetime, timezone

import httpx

from crypto_claw_engine.data.base import DerivSnapshot, OHLCVBar
from crypto_claw_engine.errors import DataGap

SPOT_URL = "https://api.binance.com"
FUT_URL = "https://fapi.binance.com"


def _to_symbol(asset: str) -> str:
    return f"{asset.upper()}USDT"


class BinanceAdapter:
    def __init__(self, client: httpx.Client | None = None, timeout: float = 10.0):
        self._client = client or httpx.Client(timeout=timeout)

    def get_ohlcv(self, asset: str, interval: str = "1d", limit: int = 100) -> list[OHLCVBar]:
        symbol = _to_symbol(asset)
        try:
            r = self._client.get(
                f"{SPOT_URL}/api/v3/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit},
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("binance", symbol, f"klines http error: {e}") from e

        rows = r.json()
        if not rows:
            raise DataGap("binance", symbol, "empty klines response")

        return [
            OHLCVBar(
                open_time=datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            for row in rows
        ]

    def get_funding(self, asset: str, limit: int = 30) -> list[DerivSnapshot]:
        symbol = _to_symbol(asset)
        try:
            r = self._client.get(
                f"{FUT_URL}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": limit},
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("binance", symbol, f"funding http error: {e}") from e

        rows = r.json()
        if not rows:
            raise DataGap("binance", symbol, "empty funding response")

        return [
            DerivSnapshot(
                symbol=row["symbol"],
                funding_rate=float(row["fundingRate"]),
                as_of=datetime.fromtimestamp(row["fundingTime"] / 1000, tz=timezone.utc),
            )
            for row in rows
        ]

    def get_open_interest(self, asset: str) -> DerivSnapshot:
        symbol = _to_symbol(asset)
        try:
            r = self._client.get(
                f"{FUT_URL}/fapi/v1/openInterest",
                params={"symbol": symbol},
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("binance", symbol, f"OI http error: {e}") from e

        data = r.json()
        return DerivSnapshot(
            symbol=data["symbol"],
            funding_rate=0.0,
            open_interest_usd=None,
            as_of=datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc),
        )
