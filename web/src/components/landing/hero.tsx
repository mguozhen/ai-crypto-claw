"use client";

import { useLocale } from "@/i18n/LocaleProvider";

export function Hero() {
  const { t } = useLocale();
  return (
    <section className="relative pt-28 pb-24 px-6 gradient-mesh overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative max-w-6xl mx-auto">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-xs font-medium mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse-glow" />
            {t("hero.badge")}
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white leading-[1.1] mb-6">
            {t("hero.title.line1")}{" "}
            <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              {t("hero.title.highlight")}
            </span>
          </h1>

          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            {t("hero.subtitle")}
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <a
              href="/download"
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold text-base hover:opacity-90 transition shadow-lg shadow-cyan-500/20"
            >
              {t("hero.cta.primary")}
            </a>
            <a
              href="#promo"
              className="px-8 py-3.5 rounded-xl border border-zinc-700 text-zinc-300 font-medium text-base hover:border-zinc-500 hover:text-white transition"
            >
              ▶ {t("hero.cta.secondary")}
            </a>
          </div>
        </div>

        {/* Promo video — full bleed inside hero, autoplay muted loop */}
        <div
          id="promo"
          className="relative mx-auto max-w-4xl rounded-2xl overflow-hidden border border-zinc-800 shadow-2xl shadow-cyan-500/10"
        >
          <video
            src="/promo.mp4"
            autoPlay
            muted
            loop
            playsInline
            poster="/logo.jpg"
            className="w-full h-auto aspect-video object-cover"
          />
        </div>

        <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
          <div>
            <div className="text-2xl font-bold text-white">6</div>
            <div className="text-xs text-zinc-500 mt-1">{t("hero.stats.agents")}</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white">3-Layer</div>
            <div className="text-xs text-zinc-500 mt-1">{t("hero.stats.dag")}</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white">24/7</div>
            <div className="text-xs text-zinc-500 mt-1">{t("hero.stats.auto")}</div>
          </div>
        </div>
      </div>
    </section>
  );
}
