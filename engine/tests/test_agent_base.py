from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import AgentSignal, Portfolio, RunRequest


class DummyAgent(AgentBase):
    name = "dummy"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance="neutral",
            confidence=0.5,
            rationale="dummy",
            evidence={"x": 1},
        )


def test_agent_base_run_for_all_assets():
    req = RunRequest(universe=["BTC", "ETH"], portfolio=Portfolio(cash_usd=1000))
    ctx = AgentContext(request=req, data={}, llm=FakeLLM())
    agent = DummyAgent()
    signals = agent.run(ctx)
    assert len(signals) == 2
    assert {s.asset for s in signals} == {"BTC", "ETH"}
    assert all(s.agent == "dummy" for s in signals)
