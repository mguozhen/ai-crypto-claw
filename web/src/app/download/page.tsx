"use client";

import Image from "next/image";
import Link from "next/link";

import { Footer } from "@/components/landing/footer";
import { Header } from "@/components/landing/header";
import { useLocale } from "@/i18n/LocaleProvider";

const ANDROID_APK_URL =
  process.env.NEXT_PUBLIC_ANDROID_APK_URL ??
  "https://expo.dev/artifacts/eas/sJYXwNUcM9YJsQZAdD5KSK.apk";
const IOS_TESTFLIGHT_URL = process.env.NEXT_PUBLIC_IOS_TESTFLIGHT_URL ?? "";
const EXPO_GO_TUNNEL =
  process.env.NEXT_PUBLIC_EXPO_GO_TUNNEL ?? "exp://dev.btcmind.ai";
const EXPO_GO_HTTPS = EXPO_GO_TUNNEL.replace(/^exp:/, "https:");

export default function DownloadPage() {
  const { t } = useLocale();

  return (
    <>
      <Header />
      <main className="min-h-screen pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white text-center mb-4">
            {t("download.heading")}
          </h1>
          <p className="text-zinc-400 text-center max-w-2xl mx-auto mb-16">
            {t("download.subtitle")}
          </p>

          {/* Expo Go QR — fastest path to a real device */}
          <div className="mb-12 rounded-2xl border border-cyan-500/20 bg-gradient-to-b from-cyan-500/5 to-transparent p-8">
            <div className="flex flex-col md:flex-row items-center gap-8">
              <div className="bg-white p-3 rounded-xl">
                <Image
                  src="/expo-go-qr.png"
                  alt="Expo Go QR"
                  width={200}
                  height={200}
                  unoptimized
                  priority
                />
              </div>
              <div className="flex-1 text-center md:text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-medium mb-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                  {t("download.expo.badge")}
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  {t("download.expo.title")}
                </h2>
                <p className="text-zinc-400 text-sm leading-relaxed mb-4">
                  {t("download.expo.body")}{" "}
                  <a
                    href="https://apps.apple.com/app/expo-go/id982107779"
                    className="text-cyan-400 hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Expo Go
                  </a>
                </p>
                <p className="text-xs text-zinc-500 break-all">
                  {t("download.expo.linkPrefix")}
                  <a
                    href={EXPO_GO_HTTPS}
                    className="text-cyan-400 hover:underline ml-1"
                  >
                    {EXPO_GO_TUNNEL}
                  </a>
                </p>
              </div>
            </div>
          </div>

          <h2 className="text-xl font-semibold text-white text-center mb-6">
            {t("download.altHeading")}
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <PlatformCard
              title="iOS"
              subtitle={t("download.ios.subtitle")}
              primary={
                IOS_TESTFLIGHT_URL
                  ? { label: t("download.ios.primary"), href: IOS_TESTFLIGHT_URL }
                  : { label: t("download.ios.primaryDisabled"), href: "#", disabled: true }
              }
              secondary={{
                label: t("download.ios.secondary"),
                href: "https://apps.apple.com/app/expo-go/id982107779",
              }}
              note={IOS_TESTFLIGHT_URL ? t("download.ios.note") : t("download.ios.noteFallback")}
            />

            <PlatformCard
              title="Android"
              subtitle={t("download.android.subtitle")}
              primary={
                ANDROID_APK_URL
                  ? { label: t("download.android.primary"), href: ANDROID_APK_URL }
                  : { label: t("download.android.primaryDisabled"), href: "#", disabled: true }
              }
              secondary={{
                label: t("download.android.secondary"),
                href: "https://play.google.com/store/apps/details?id=host.exp.exponent",
              }}
              note={
                ANDROID_APK_URL
                  ? t("download.android.note")
                  : t("download.android.noteFallback")
              }
            />
          </div>

          <div className="mt-16 max-w-2xl mx-auto rounded-2xl border border-white/5 bg-white/[0.02] p-6">
            <h2 className="text-white font-semibold mb-3">
              {t("download.steps.heading")}
            </h2>
            <ol className="space-y-3 text-sm text-zinc-400 list-decimal list-inside">
              <li>{t("download.steps.1")}</li>
              <li>{t("download.steps.2")}</li>
              <li>{t("download.steps.3")}</li>
              <li>{t("download.steps.4")}</li>
            </ol>
          </div>

          <p className="mt-12 text-center text-sm text-zinc-500">
            {t("download.invite.text")}
            <Link href="/" className="text-cyan-400 hover:text-cyan-300 ml-1">
              {t("download.invite.cta")}
            </Link>
          </p>
        </div>
      </main>
      <Footer />
    </>
  );
}

function PlatformCard({
  title,
  subtitle,
  primary,
  secondary,
  note,
}: {
  title: string;
  subtitle: string;
  primary: { label: string; href: string; disabled?: boolean };
  secondary?: { label: string; href: string };
  note: string;
}) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-8 flex flex-col">
      <div className="flex items-baseline justify-between mb-1">
        <h3 className="text-2xl font-bold text-white">{title}</h3>
      </div>
      <p className="text-sm text-zinc-500 mb-6">{subtitle}</p>

      {primary.disabled ? (
        <button
          disabled
          className="w-full px-6 py-3 rounded-xl border border-zinc-800 bg-zinc-900/50 text-zinc-500 font-medium text-sm cursor-not-allowed"
        >
          {primary.label}
        </button>
      ) : (
        <a
          href={primary.href}
          className="w-full text-center px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold text-sm hover:opacity-90 transition shadow-lg shadow-cyan-500/20"
        >
          {primary.label}
        </a>
      )}

      {secondary && (
        <a
          href={secondary.href}
          target="_blank"
          rel="noreferrer"
          className="mt-3 w-full text-center px-6 py-3 rounded-xl border border-zinc-800 text-zinc-300 font-medium text-sm hover:border-zinc-600 hover:text-white transition"
        >
          {secondary.label}
        </a>
      )}

      <p className="mt-6 text-xs text-zinc-500 leading-relaxed">{note}</p>
    </div>
  );
}
