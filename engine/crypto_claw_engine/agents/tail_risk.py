import math

from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


def _log_returns(closes: list[float]) -> list[float]:
    out = []
    for i in range(1, len(closes)):
        if closes[i - 1] <= 0:
            continue
        out.append(math.log(closes[i] / closes[i - 1]))
    return out


def _stdev(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var)


class TailRiskAgent(AgentBase):
    name = "tail_risk"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        bars = (ctx.data.get("ohlcv") or {}).get(asset) or []
        if len(bars) < 60:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.0,
                rationale="Data unavailable (need >=60 bars for regime analysis).",
                evidence={"bars": len(bars)},
            )

        closes = [b.close for b in bars]
        rets = _log_returns(closes)
        vol_30 = _stdev(rets[-30:])
        vol_60 = _stdev(rets[-60:])
        regime_shift = (vol_30 / vol_60 - 1.0) if vol_60 > 0 else 0.0

        window = closes[-60:]
        peak = max(window)
        peak_idx = window.index(peak)
        trough_after_peak = min(window[peak_idx:])
        max_dd = (trough_after_peak - peak) / peak if peak else 0.0

        stance = "neutral"
        confidence = 0.5
        if regime_shift > 0.3 or max_dd < -0.2:
            stance = "bearish"
            confidence = min(0.6 + max(regime_shift, abs(max_dd)), 0.95)
        elif regime_shift < -0.3 and max_dd > -0.05:
            stance = "bullish"
            confidence = 0.6

        evidence = {
            "vol_30d": round(vol_30, 5),
            "vol_60d": round(vol_60, 5),
            "regime_shift": round(regime_shift, 3),
            "max_drawdown": round(max_dd, 3),
        }

        rationale = (
            ctx.llm.complete(
                messages=[
                    {
                        "role": "user",
                        "content": f"Tail risk for {asset}: {evidence}. Stance: {stance}.",
                    }
                ],
                tag="tail_risk",
            )
            if ctx.llm
            else f"{asset} tail risk {stance}; evidence: {evidence}"
        )

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
        )
