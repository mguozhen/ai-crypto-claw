import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click

from crypto_claw_engine.data.base import DerivSnapshot, OHLCVBar
from crypto_claw_engine.data.binance import BinanceAdapter
from crypto_claw_engine.data.coingecko import CoinGeckoAdapter
from crypto_claw_engine.graph.runner import run_engine
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


def _fake_price_source():
    class FakePrice:
        def get_ohlcv(self, asset, interval, limit):
            base = datetime(2026, 1, 1, tzinfo=timezone.utc)
            return [
                OHLCVBar(
                    open_time=base + timedelta(days=i),
                    open=100 + i,
                    high=100 + i + 1,
                    low=100 + i - 1,
                    close=100 + i * 1.5,
                    volume=10.0,
                )
                for i in range(80)
            ]

    return FakePrice()


def _fake_deriv_source():
    class FakeDeriv:
        def get_funding(self, asset, limit):
            return [
                DerivSnapshot(
                    symbol=f"{asset}USDT",
                    funding_rate=0.0005,
                    as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
                )
                for _ in range(10)
            ]

    return FakeDeriv()


def _load_portfolio(path: str | None) -> Portfolio:
    if not path:
        return Portfolio(cash_usd=10_000.0)
    data = json.loads(Path(path).read_text())
    return Portfolio(**data)


@click.group()
def main():
    """AI-Crypto-Claw engine CLI."""


@main.command()
@click.option("--universe", required=True, help="Comma-separated ticker list, e.g. BTC,ETH,SOL")
@click.option("--horizon", default="daily", type=click.Choice(["intraday", "daily", "weekly"]))
@click.option("--portfolio-file", default=None, help="Path to portfolio JSON file")
@click.option("--json", "as_json", is_flag=True, help="Dump machine-readable JSON")
def analyze(universe, horizon, portfolio_file, as_json):
    """Run the council against the given universe and print decisions."""
    assets = [a.strip().upper() for a in universe.split(",") if a.strip()]
    portfolio = _load_portfolio(portfolio_file)
    request = RunRequest(universe=assets, horizon=horizon, portfolio=portfolio)

    if os.environ.get("CRYPTO_CLAW_FAKE_DATA") == "1":
        price_source = _fake_price_source()
        deriv_source = _fake_deriv_source()
    else:
        price_source = BinanceAdapter()
        deriv_source = BinanceAdapter()
        _ = CoinGeckoAdapter()

    result = run_engine(
        request=request,
        price_source=price_source,
        deriv_source=deriv_source,
        llm=FakeLLM(),
    )

    if as_json:
        click.echo(result.model_dump_json())
        return

    click.echo(f"\n=== AI-Crypto-Claw run {result.run_id} @ {result.as_of.isoformat()} ===\n")
    for d in result.decisions:
        action_upper = d.action.upper()
        click.echo(f"Decision: {d.asset} {action_upper}  size={d.size_pct:+.2f}  conf={d.confidence:.2f}")
        click.echo(f"  reasoning: {d.reasoning}")
        for s in d.contributing_signals:
            click.echo(f"    [{s.agent}] {s.stance}  conf={s.confidence:.2f}  {s.rationale[:80]}")
        click.echo("")
    if result.agents_failed:
        click.echo(f"agents_failed: {result.agents_failed}")
