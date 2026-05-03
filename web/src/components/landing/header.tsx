"use client";

import { useLocale } from "@/i18n/LocaleProvider";

import { LocaleSwitcher } from "./locale-switcher";

export function Header() {
  const { t } = useLocale();
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 backdrop-blur-xl bg-[#0a0a0f]/80">
      <nav className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2">
          <img
            src="/logo.jpg"
            alt="btcmind"
            className="w-9 h-9 rounded-lg ring-1 ring-white/10"
          />
          <span className="font-semibold text-lg text-white">{t("brand.name")}</span>
        </a>

        <div className="hidden md:flex items-center gap-8 text-sm text-zinc-400">
          <a href="/#features" className="hover:text-white transition">
            {t("nav.features")}
          </a>
          <a href="/#agents" className="hover:text-white transition">
            {t("nav.agents")}
          </a>
          <a href="/#pricing" className="hover:text-white transition">
            {t("nav.pricing")}
          </a>
          <a href="/download" className="hover:text-white transition">
            {t("nav.download")}
          </a>
          <a
            href="https://t.me/jingyao04_bot"
            target="_blank"
            rel="noreferrer"
            className="hover:text-white transition"
          >
            {t("nav.telegram")}
          </a>
        </div>

        <div className="flex items-center gap-3">
          <LocaleSwitcher />
          <a
            href="/dashboard"
            className="text-sm text-zinc-300 hover:text-white transition px-4 py-2"
          >
            {t("nav.login")}
          </a>
          <a
            href="/download"
            className="text-sm font-medium bg-gradient-to-r from-cyan-500 to-purple-500 text-white px-4 py-2 rounded-lg hover:opacity-90 transition"
          >
            {t("nav.getApp")}
          </a>
        </div>
      </nav>
    </header>
  );
}
