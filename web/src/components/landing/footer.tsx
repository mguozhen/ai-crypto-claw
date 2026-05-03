"use client";

import { useLocale } from "@/i18n/LocaleProvider";

export function Footer() {
  const { t } = useLocale();
  return (
    <footer className="border-t border-white/5 py-12 px-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <img src="/logo.jpg" alt="btcmind" className="w-7 h-7 rounded-md ring-1 ring-white/10" />
          <span className="text-sm text-zinc-400">{t("footer.tagline")}</span>
        </div>

        <div className="flex items-center gap-6 text-xs text-zinc-500">
          <a
            href="https://github.com/mguozhen/ai-crypto-claw"
            target="_blank"
            rel="noreferrer"
            className="hover:text-zinc-300 transition"
          >
            GitHub
          </a>
          <a
            href="https://t.me/jingyao04_bot"
            target="_blank"
            rel="noreferrer"
            className="hover:text-zinc-300 transition"
          >
            Telegram
          </a>
        </div>

        <div className="text-xs text-zinc-600">{t("footer.copy")}</div>
      </div>
    </footer>
  );
}
