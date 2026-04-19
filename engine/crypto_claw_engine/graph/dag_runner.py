"""
DAG Runner — parallel execution of agents in topological layers.
Layer 0: Technicals, Derivatives, TailRisk, Reflection (parallel)
Layer 1: BullResearcher, BearResearcher (parallel, after layer 0)
Layer 2: PortfolioManager (after layer 1)
"""
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal

logger = logging.getLogger(__name__)


class DAGRunner:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def run_agents(
        self,
        agents_by_layer: dict[int, list[AgentBase]],
        ctx: AgentContext,
    ) -> tuple[list[AgentSignal], list[str]]:
        """
        Execute agents layer by layer. Within each layer, agents run in parallel.
        Returns (all_signals, failed_agent_names).
        """
        all_signals: list[AgentSignal] = []
        failed: list[str] = []

        for layer_num in sorted(agents_by_layer.keys()):
            layer_agents = agents_by_layer[layer_num]
            logger.info(f"DAG Layer {layer_num}: running {[a.name for a in layer_agents]}")

            # Inject upstream signals into context for this layer
            layer_ctx = AgentContext(
                request=ctx.request,
                data={**ctx.data, "upstream_signals": all_signals},
                llm=ctx.llm,
            )

            if len(layer_agents) == 1:
                # Single agent, no need for thread pool
                agent = layer_agents[0]
                try:
                    signals = agent.run(layer_ctx)
                    all_signals.extend(signals)
                except Exception as e:
                    logger.error(f"Agent {agent.name} failed: {e}")
                    failed.append(agent.name)
            else:
                # Parallel execution
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {
                        executor.submit(agent.run, layer_ctx): agent
                        for agent in layer_agents
                    }
                    for future in as_completed(futures):
                        agent = futures[future]
                        try:
                            signals = future.result(timeout=60)
                            all_signals.extend(signals)
                        except Exception as e:
                            logger.error(f"Agent {agent.name} failed: {e}")
                            failed.append(agent.name)

        return all_signals, failed
