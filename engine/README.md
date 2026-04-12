# crypto-claw-engine

Pure Python engine for AI-Crypto-Claw. Stateless. No Hermes or FastAPI dependency. See `../docs/superpowers/specs/2026-04-11-ai-crypto-claw-design.md`.

## Install (editable)

    cd engine && pip install -e ".[dev]"

## Run

    python -m crypto_claw_engine analyze --universe BTC,ETH,SOL

## Test

    pytest                    # unit tests only
    pytest -m live            # hit real CoinGecko + Binance
