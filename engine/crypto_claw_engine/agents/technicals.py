import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


class TechnicalsAgent(AgentBase):
    name = "technicals"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        bars = (ctx.data.get("ohlcv") or {}).get(asset) or []
        if len(bars) < 20:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.0,
                rationale="Data unavailable (not enough OHLCV bars).",
                evidence={"bars": len(bars)},
            )

        df = pd.DataFrame(
            {
                "open": [b.open for b in bars],
                "high": [b.high for b in bars],
                "low": [b.low for b in bars],
                "close": [b.close for b in bars],
                "volume": [b.volume for b in bars],
            }
        )

        rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]
        atr = AverageTrueRange(df["high"], df["low"], df["close"], window=14).average_true_range().iloc[-1]
        last = df["close"].iloc[-1]
        past = df["close"].iloc[-20]
        trend = (last - past) / past if past else 0.0
        volatility = (atr / last) if last else 0.0

        stance = "neutral"
        confidence = 0.5
        if (rsi < 35 and trend > 0) or trend > 0.05:
            stance = "bullish"
            if rsi < 35:
                confidence += 0.2
            if trend > 0.05:
                confidence += 0.15
        elif (rsi > 70 and trend < 0) or trend < -0.05:
            stance = "bearish"
            if rsi > 70:
                confidence += 0.2
            if trend < -0.05:
                confidence += 0.15

        confidence = min(confidence, 1.0)

        evidence = {
            "rsi": round(float(rsi), 2),
            "trend_20d_pct": round(float(trend) * 100, 2),
            "atr_pct": round(float(volatility) * 100, 2),
            "last_close": round(float(last), 2),
        }

        rationale = (
            ctx.llm.complete(
                messages=[
                    {
                        "role": "user",
                        "content": f"Assess {asset} from evidence: {evidence}. Stance: {stance}.",
                    }
                ],
                tag="technicals",
            )
            if ctx.llm
            else f"{asset} technicals {stance}; evidence: {evidence}"
        )

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
        )
