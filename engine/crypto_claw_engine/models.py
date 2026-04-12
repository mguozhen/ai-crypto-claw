from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Stance = Literal["bullish", "bearish", "neutral"]
Action = Literal["buy", "sell", "hold", "close"]
Horizon = Literal["intraday", "daily", "weekly"]
ModelTier = Literal["cheap", "mid", "best"]


class Portfolio(BaseModel):
    cash_usd: float = 0.0
    holdings: dict[str, float] = Field(default_factory=dict)  # symbol -> units


class RunRequest(BaseModel):
    universe: list[str]
    horizon: Horizon = "daily"
    as_of: datetime | None = None
    portfolio: Portfolio = Field(default_factory=Portfolio)
    agents_enabled: list[str] | None = None
    llm_model_tier: ModelTier | None = None


class AgentSignal(BaseModel):
    agent: str
    asset: str
    stance: Stance
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    evidence: dict


class Decision(BaseModel):
    asset: str
    action: Action
    size_pct: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    contributing_signals: list[AgentSignal] = Field(default_factory=list)
    risk_notes: str = ""


class RunResult(BaseModel):
    run_id: str
    as_of: datetime
    signals: list[AgentSignal]
    decisions: list[Decision]
    cost_usd: float = 0.0
    agents_failed: list[str] = Field(default_factory=list)
