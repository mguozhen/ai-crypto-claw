/**
 * Dashboard landing. Two purposes:
 *   1. End-state for users coming from btcmind.ai homepage CTA — placeholder
 *      until the full web dashboard ships.
 *   2. Mobile→web handoff: when ?handoff=<token> is present, redirect through
 *      the FastAPI exchange so the user lands authenticated.
 *
 * Implemented as a client component so static export (output:"export") can
 * still pre-render this route — `searchParams` are read from window at runtime.
 */
"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api-production-44a75.up.railway.app";

export default function DashboardPage() {
  const [handoffSeen, setHandoffSeen] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const handoff = params.get("handoff");
    const action = params.get("action");
    if (handoff) {
      setHandoffSeen(true);
      const next = action ? `/?action=${encodeURIComponent(action)}` : "/";
      const exchange = `${API_BASE}/v1/auth/web-exchange?handoff=${encodeURIComponent(
        handoff,
      )}&next=${encodeURIComponent(next)}`;
      window.location.replace(exchange);
    }
  }, []);

  if (handoffSeen) {
    return (
      <main className="min-h-screen flex items-center justify-center p-8 text-zinc-400">
        Signing you in…
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-md text-center space-y-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
          Dashboard coming soon
        </h1>
        <p className="text-zinc-400">
          The full web dashboard is in development. In the meantime you can install
          the iOS/Android app and view your portfolio there.
        </p>
        <a
          href="/download"
          className="inline-block px-5 py-2.5 rounded-lg bg-cyan-400 text-black font-semibold"
        >
          Get the app
        </a>
        <a href="/" className="block text-cyan-400 underline text-sm">
          ← Back to home
        </a>
      </div>
    </main>
  );
}
