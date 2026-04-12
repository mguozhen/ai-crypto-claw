import httpx
import pytest
import respx

from crypto_claw_engine.data.coingecko import CoinGeckoAdapter
from crypto_claw_engine.errors import DataGap


def test_get_price_known_symbol(load_fixture):
    with respx.mock(base_url="https://api.coingecko.com/api/v3") as mock:
        mock.get("/simple/price").mock(
            return_value=httpx.Response(200, json=load_fixture("coingecko_simple_price.json"))
        )
        adapter = CoinGeckoAdapter()
        snap = adapter.get_price("BTC")
        assert snap.symbol == "BTC"
        assert snap.price_usd == 65000.0
        assert snap.market_cap_usd == 1280000000000.0


def test_get_price_unknown_symbol_raises_data_gap():
    with respx.mock(base_url="https://api.coingecko.com/api/v3") as mock:
        mock.get("/simple/price").mock(return_value=httpx.Response(200, json={}))
        adapter = CoinGeckoAdapter()
        with pytest.raises(DataGap) as exc:
            adapter.get_price("BTC")
        assert exc.value.source == "coingecko"


def test_get_price_http_error_raises_data_gap():
    with respx.mock(base_url="https://api.coingecko.com/api/v3") as mock:
        mock.get("/simple/price").mock(return_value=httpx.Response(500))
        adapter = CoinGeckoAdapter()
        with pytest.raises(DataGap):
            adapter.get_price("BTC")
