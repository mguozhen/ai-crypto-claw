from dataclasses import dataclass, field
from typing import Any

from crypto_claw_engine.llm import LLMClient
from crypto_claw_engine.models import AgentSignal, RunRequest


@dataclass
class AgentContext:
    request: RunRequest
    data: dict[str, Any] = field(default_factory=dict)
    llm: LLMClient | None = None


class AgentBase:
    name: str = "base"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        raise NotImplementedError

    def run(self, ctx: AgentContext) -> list[AgentSignal]:
        out: list[AgentSignal] = []
        for asset in ctx.request.universe:
            out.append(self.analyze(asset, ctx))
        return out
