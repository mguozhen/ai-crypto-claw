from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class PriceSnapshot(BaseModel):
    symbol: str
    price_usd: float
    market_cap_usd: float | None = None
    volume_24h_usd: float | None = None


class OHLCVBar(BaseModel):
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class DerivSnapshot(BaseModel):
    symbol: str
    funding_rate: float
    open_interest_usd: float | None = None
    as_of: datetime


class PriceSource(Protocol):
    def get_price(self, symbol: str) -> PriceSnapshot: ...
    def get_ohlcv(self, symbol: str, interval: str, limit: int) -> list[OHLCVBar]: ...


class DerivSource(Protocol):
    def get_funding(self, symbol: str, limit: int) -> list[DerivSnapshot]: ...
    def get_open_interest(self, symbol: str) -> DerivSnapshot: ...
