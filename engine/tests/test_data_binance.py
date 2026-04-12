import httpx
import pytest
import respx

from crypto_claw_engine.data.binance import BinanceAdapter
from crypto_claw_engine.errors import DataGap


def test_get_ohlcv_parses_klines(load_fixture):
    with respx.mock() as mock:
        mock.get("https://api.binance.com/api/v3/klines").mock(
            return_value=httpx.Response(200, json=load_fixture("binance_klines_btc.json"))
        )
        adapter = BinanceAdapter()
        bars = adapter.get_ohlcv("BTC", interval="1d", limit=3)
        assert len(bars) == 3
        assert bars[0].open == 64000.0
        assert bars[0].close == 65000.0
        assert bars[-1].close == 66500.0


def test_get_funding_parses(load_fixture):
    with respx.mock() as mock:
        mock.get("https://fapi.binance.com/fapi/v1/fundingRate").mock(
            return_value=httpx.Response(200, json=load_fixture("binance_funding_btc.json"))
        )
        adapter = BinanceAdapter()
        snaps = adapter.get_funding("BTC", limit=3)
        assert len(snaps) == 3
        assert snaps[0].funding_rate == 0.0001
        assert snaps[0].symbol == "BTCUSDT"


def test_get_open_interest_parses(load_fixture):
    with respx.mock() as mock:
        mock.get("https://fapi.binance.com/fapi/v1/openInterest").mock(
            return_value=httpx.Response(200, json=load_fixture("binance_oi_btc.json"))
        )
        adapter = BinanceAdapter()
        snap = adapter.get_open_interest("BTC")
        assert snap.funding_rate == 0.0
        assert snap.open_interest_usd is None or snap.open_interest_usd > 0


def test_ohlcv_http_error_raises_data_gap():
    with respx.mock() as mock:
        mock.get("https://api.binance.com/api/v3/klines").mock(return_value=httpx.Response(503))
        adapter = BinanceAdapter()
        with pytest.raises(DataGap):
            adapter.get_ohlcv("BTC", interval="1d", limit=3)
