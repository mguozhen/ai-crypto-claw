import json

from click.testing import CliRunner

from crypto_claw_engine.cli import main


def test_cli_analyze_runs_with_fakes(monkeypatch):
    monkeypatch.setenv("CRYPTO_CLAW_FAKE_DATA", "1")
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--universe", "BTC,ETH", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output.strip().splitlines()[-1])
    assert "decisions" in payload
    assert {d["asset"] for d in payload["decisions"]} == {"BTC", "ETH"}


def test_cli_human_summary(monkeypatch):
    monkeypatch.setenv("CRYPTO_CLAW_FAKE_DATA", "1")
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--universe", "BTC"])
    assert result.exit_code == 0
    assert "BTC" in result.output
    assert "Decision" in result.output or "decision" in result.output.lower()
