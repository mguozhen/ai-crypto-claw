"use client";

import { useLocale } from "@/i18n/LocaleProvider";

export function CTA() {
  const { t } = useLocale();
  return (
    <section className="py-24 px-6">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          {t("cta.title")}
        </h2>
        <p className="text-zinc-400 mb-8 max-w-xl mx-auto">{t("cta.subtitle")}</p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="/download"
            className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold hover:opacity-90 transition shadow-lg shadow-cyan-500/20"
          >
            {t("cta.button")}
          </a>
          <a
            href="https://t.me/+h1zpoMhqydtjYjVl"
            target="_blank"
            rel="noreferrer"
            className="px-8 py-3.5 rounded-xl border border-zinc-700 text-zinc-300 font-medium hover:border-zinc-500 hover:text-white transition"
          >
            {t("nav.telegram")}
          </a>
          <a
            href="https://discord.gg/A6s4U5TbS"
            target="_blank"
            rel="noreferrer"
            className="px-8 py-3.5 rounded-xl border border-zinc-700 text-zinc-300 font-medium hover:border-zinc-500 hover:text-white transition"
          >
            {t("nav.discord")}
          </a>
        </div>

        <p className="text-xs text-zinc-600 mt-6">{t("footer.copy")}</p>
      </div>
    </section>
  );
}
