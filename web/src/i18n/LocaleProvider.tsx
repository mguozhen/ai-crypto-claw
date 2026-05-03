"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { DEFAULT_LOCALE, LOCALES, type Locale, t as tRaw } from "./messages";

const STORAGE_KEY = "btcmind.locale";

type Ctx = {
  locale: Locale;
  setLocale: (next: Locale) => void;
  t: (key: string) => string;
};

const LocaleContext = createContext<Ctx>({
  locale: DEFAULT_LOCALE,
  setLocale: () => undefined,
  t: (key) => tRaw(DEFAULT_LOCALE, key),
});

function detect(): Locale {
  if (typeof window === "undefined") return DEFAULT_LOCALE;
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored && (LOCALES as readonly string[]).includes(stored)) return stored as Locale;
  const nav = (window.navigator?.language || "").toLowerCase();
  if (nav.startsWith("ja")) return "ja";
  if (nav.startsWith("zh")) return "zh";
  if (nav.startsWith("en")) return "en";
  return DEFAULT_LOCALE;
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  // Render in default locale during SSG; swap to detected on mount to avoid hydration mismatch.
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    setLocaleState(detect());
  }, []);

  const setLocale = (next: Locale) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, next);
      window.document.documentElement.lang = next;
    }
    setLocaleState(next);
  };

  const value: Ctx = {
    locale,
    setLocale,
    t: (key) => tRaw(locale, key),
  };

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  return useContext(LocaleContext);
}
