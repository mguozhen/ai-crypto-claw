from datetime import datetime, timezone

from crypto_claw_engine.data.base import (
    DerivSnapshot,
    OHLCVBar,
    PriceSnapshot,
)


def test_price_snapshot_fields():
    s = PriceSnapshot(symbol="BTC", price_usd=65000.0, market_cap_usd=1.3e12, volume_24h_usd=3.5e10)
    assert s.symbol == "BTC"


def test_ohlcv_bar_fields():
    bar = OHLCVBar(
        open_time=datetime(2026, 4, 10, tzinfo=timezone.utc),
        open=64000,
        high=65500,
        low=63800,
        close=65000,
        volume=12345.6,
    )
    assert bar.close == 65000


def test_deriv_snapshot_fields():
    d = DerivSnapshot(
        symbol="BTCUSDT",
        funding_rate=0.0001,
        open_interest_usd=1.2e10,
        as_of=datetime(2026, 4, 10, tzinfo=timezone.utc),
    )
    assert d.funding_rate == 0.0001
