export function AgentFlow() {
  return (
    <section id="agents" className="py-24 px-6 gradient-mesh">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            3-Layer Agent Pipeline
          </h2>
          <p className="text-zinc-400 max-w-xl mx-auto">
            Every analysis runs through a structured DAG — parallel research,
            adversarial debate, then unified decision.
          </p>
        </div>

        {/* DAG Visualization */}
        <div className="relative max-w-3xl mx-auto">
          {/* Layer 0 */}
          <div className="mb-4">
            <div className="text-xs text-zinc-500 font-mono mb-3 uppercase tracking-wider">
              Layer 0 — Parallel Analysis
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <AgentCard name="Technicals" detail="RSI, MACD, ATR" color="cyan" />
              <AgentCard name="Derivatives" detail="Funding, OI" color="cyan" />
              <AgentCard name="TailRisk" detail="VaR, Drawdown" color="cyan" />
              <AgentCard name="Reflection" detail="History Review" color="cyan" />
            </div>
          </div>

          {/* Arrow down */}
          <div className="flex justify-center py-4">
            <div className="w-px h-8 bg-gradient-to-b from-cyan-500/50 to-purple-500/50" />
          </div>

          {/* Layer 1 */}
          <div className="mb-4">
            <div className="text-xs text-zinc-500 font-mono mb-3 uppercase tracking-wider">
              Layer 1 — Adversarial Debate
            </div>
            <div className="grid grid-cols-2 gap-3 max-w-md mx-auto">
              <AgentCard name="Bull Researcher" detail="Bullish case" color="green" />
              <AgentCard name="Bear Researcher" detail="Bearish case" color="red" />
            </div>
            <div className="text-center mt-2 text-xs text-zinc-600">
              Both cite upstream signals as evidence
            </div>
          </div>

          {/* Arrow down */}
          <div className="flex justify-center py-4">
            <div className="w-px h-8 bg-gradient-to-b from-purple-500/50 to-cyan-500/50" />
          </div>

          {/* Layer 2 */}
          <div>
            <div className="text-xs text-zinc-500 font-mono mb-3 uppercase tracking-wider">
              Layer 2 — Final Decision
            </div>
            <div className="max-w-xs mx-auto">
              <div className="gradient-border p-4 rounded-xl text-center glow-purple">
                <div className="text-sm font-semibold text-white">Portfolio Manager</div>
                <div className="text-xs text-zinc-400 mt-1">
                  long / short / flat + size% + confidence
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function AgentCard({
  name,
  detail,
  color,
}: {
  name: string;
  detail: string;
  color: "cyan" | "green" | "red";
}) {
  const borderColors = {
    cyan: "border-cyan-500/20 hover:border-cyan-500/40",
    green: "border-green-500/20 hover:border-green-500/40",
    red: "border-red-500/20 hover:border-red-500/40",
  };
  const dotColors = {
    cyan: "bg-cyan-400",
    green: "bg-green-400",
    red: "bg-red-400",
  };

  return (
    <div
      className={`border ${borderColors[color]} bg-[#111118] rounded-lg p-3 transition-colors`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className={`w-1.5 h-1.5 rounded-full ${dotColors[color]}`} />
        <span className="text-xs font-medium text-white">{name}</span>
      </div>
      <div className="text-[10px] text-zinc-500">{detail}</div>
    </div>
  );
}
