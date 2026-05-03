"use client";

import { LOCALES, LOCALE_LABELS, type Locale } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";

export function LocaleSwitcher() {
  const { locale, setLocale } = useLocale();
  return (
    <div className="hidden md:inline-flex items-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900/40 p-0.5 text-xs">
      {LOCALES.map((l: Locale) => (
        <button
          key={l}
          type="button"
          onClick={() => setLocale(l)}
          className={`px-2 py-1 rounded-md transition ${
            l === locale
              ? "bg-white/10 text-white"
              : "text-zinc-500 hover:text-zinc-200"
          }`}
        >
          {LOCALE_LABELS[l]}
        </button>
      ))}
    </div>
  );
}
