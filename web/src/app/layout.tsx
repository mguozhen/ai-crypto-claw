import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { LocaleProvider } from "@/i18n/LocaleProvider";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "btcmind — AI 在为你看盘 · 决策 · 执行",
  description:
    "把「看盘」「分析」「下单」打包给 6 位 AI 专员。多 agent 议事 → 出预测 → 自动执行 → +5% 自动止盈。手机口袋里的交易桌面。",
  keywords: ["crypto", "AI trading", "auto trading", "multi-agent", "BTC", "ETH", "OKX", "btcmind", "量化交易"],
  icons: {
    icon: "/logo.jpg",
    apple: "/logo.jpg",
  },
  openGraph: {
    title: "btcmind",
    description: "6 位 AI 专员议事 → 出预测 → 自动执行 → +5% 自动止盈。",
    type: "website",
    images: ["/logo.jpg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col">
        <LocaleProvider>{children}</LocaleProvider>
      </body>
    </html>
  );
}
