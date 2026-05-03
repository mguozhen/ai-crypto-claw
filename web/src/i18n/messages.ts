/**
 * Static translation table. Keep keys flat — easier to grep, easier to diff.
 * Three locales: zh (default), en, ja. Missing keys fall back to zh.
 */
export const LOCALES = ["zh", "en", "ja"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "zh";

export const LOCALE_LABELS: Record<Locale, string> = {
  zh: "中文",
  en: "EN",
  ja: "日本語",
};

type Dict = Record<string, string>;

export const messages: Record<Locale, Dict> = {
  zh: {
    "brand.name": "btcmind",
    "nav.features": "功能",
    "nav.agents": "AI 专员",
    "nav.pricing": "价格",
    "nav.download": "下载",
    "nav.telegram": "Telegram",
    "nav.discord": "Discord",
    "nav.login": "登录",
    "nav.getApp": "下载 App",

    "hero.badge": "实时运行 · 6 个 AI 专员正在分析行情",
    "hero.title.line1": "AI 在为你",
    "hero.title.highlight": "看盘 · 决策 · 执行",
    "hero.subtitle":
      "把「看盘」「分析」「下单」打包给 6 位 AI 专员。多 agent 议事 → 出预测 → 自动执行 → +5% 自动止盈。你只需要看每天的成绩单。",
    "hero.cta.primary": "立即下载 App",
    "hero.cta.secondary": "看 1 分钟演示",
    "hero.stats.agents": "AI 专员",
    "hero.stats.dag": "三层 DAG 决策",
    "hero.stats.auto": "全天候自动执行",

    "features.title": "为什么选 btcmind",
    "features.sub": "不是「AI 行情助手」，是把交易整套流程做完。",
    "features.f1.title": "执行卡式交易建议",
    "features.f1.body":
      "每条回复给 8 段执行卡：直接结论 / 关键位 / 解读 / 行动 / 失效信号。具体到 $77K 守不守、$80K 突不突破，不打「市场有风险」那种官腔。",
    "features.f2.title": "多 agent 议事 → 真预测",
    "features.f2.body":
      "Bull / Bear researcher 辩论 + 技术派 / 衍生品 / 尾部风险 agent 并行分析 → portfolio manager 综合 BUY/SELL/HOLD + 信心度。决策可追溯。",
    "features.f3.title": "5% 自动止盈 · 3% 仓位 cap",
    "features.f3.body":
      "连接你自己的 OKX，AI 看到信号自动开仓，单笔 +5% 即刻平仓。最大持仓不超过余额 3%，宕机也不会爆。",
    "features.f4.title": "盯盘提醒 · 语音对话",
    "features.f4.body":
      "BTC 跌破 $77K 推送通知。微信式按住说话 → AI 转写 → Claw 直接回。手机口袋里的交易桌面。",

    "cta.title": "把 Claw 装进口袋",
    "cta.subtitle": "iOS（Expo Go） + Android APK 都已上线，扫码立刻试。",
    "cta.button": "前往下载",

    "download.heading": "下载 btcmind App",
    "download.subtitle":
      "把 AI 交易副驾装进口袋。语音和 Claw 对话、每日预测摘要、随时审计你的仓位。",
    "download.expo.badge": "Dev 预览 · 无需安装包",
    "download.expo.title": "扫码立刻试一下",
    "download.expo.body":
      "iPhone 用户先到 App Store 装 Expo Go，然后用相机扫描左边的二维码即可打开 btcmind。",
    "download.expo.linkPrefix": "或直接打开链接：",
    "download.altHeading": "或下载完整安装包",
    "download.ios.subtitle": "iPhone 与 iPad · iOS 16+",
    "download.ios.primary": "加入 TestFlight",
    "download.ios.primaryDisabled": "敬请期待",
    "download.ios.secondary": "或在 Expo Go 中扫码（开发预览）",
    "download.ios.note":
      "TestFlight 是公开 Beta 渠道。先在 iPhone 上装 TestFlight，然后点击上方按钮加入测试。",
    "download.ios.noteFallback":
      "App Store / TestFlight 正式版即将上线，目前请用上方 Expo Go 扫码体验完整功能。",
    "download.android.subtitle": "Android 8.0+（Oreo 起）",
    "download.android.primary": "下载 APK",
    "download.android.primaryDisabled": "构建中…",
    "download.android.secondary": "或安装 Expo Go",
    "download.android.note":
      "下载 APK 后，允许浏览器安装未知来源应用，再打开 APK 完成安装。首次启动会请求摄像头与麦克风权限。",
    "download.android.noteFallback":
      "Android 首次构建排队中，几分钟后刷新本页可获得直接下载链接。",
    "download.steps.heading": "首次使用",
    "download.steps.1": "用上方任一方式安装并打开 btcmind。",
    "download.steps.2":
      "进入「设置」→「登录」。输入邮箱与邀请码（管理员邮箱可直登），收到登录链接立即进入。",
    "download.steps.3": "开启麦克风权限，即可在聊天页按住按钮录音（仿微信，松手发送）。",
    "download.steps.4": "在「设置」打开「每日提醒」，自定义时间，每天定点收到 Claw 的预测摘要。",
    "download.invite.text": "还没有邀请码？",
    "download.invite.cta": "在首页申请内测",

    "footer.tagline": "btcmind · 你的 AI 交易副驾",
    "footer.copy": "© 2026 btcmind. 不构成投资建议。",
  },
  en: {
    "brand.name": "btcmind",
    "nav.features": "Features",
    "nav.agents": "AI Agents",
    "nav.pricing": "Pricing",
    "nav.download": "Download",
    "nav.telegram": "Telegram",
    "nav.discord": "Discord",
    "nav.login": "Log in",
    "nav.getApp": "Get the App",

    "hero.badge": "Live — 6 AI agents analyzing markets right now",
    "hero.title.line1": "AI is",
    "hero.title.highlight": "watching · deciding · executing",
    "hero.subtitle":
      "Hand off the whole flow — chart-watching, debate, order placement — to 6 AI specialists. Multi-agent council → prediction → auto-trade → +5% auto-take-profit. You just check the daily report.",
    "hero.cta.primary": "Get the App",
    "hero.cta.secondary": "Watch 1-min demo",
    "hero.stats.agents": "AI Specialists",
    "hero.stats.dag": "3-Layer DAG",
    "hero.stats.auto": "24/7 Auto-Execute",

    "features.title": "Why btcmind",
    "features.sub": "Not just another AI assistant — the entire trading loop, automated.",
    "features.f1.title": "Execution-card answers",
    "features.f1.body":
      "Every Claw reply is an 8-section execution card: verdict, key levels, structure, action plan, invalidation. Concrete: 'lose $77K → cut half, break $80K → add'. No 'be careful out there' platitudes.",
    "features.f2.title": "Multi-agent council → real predictions",
    "features.f2.body":
      "Bull / Bear researchers debate. Technical / Derivatives / Tail-risk agents run in parallel. Portfolio Manager outputs BUY/SELL/HOLD + confidence. Every decision is traceable.",
    "features.f3.title": "+5% auto take-profit · 3% position cap",
    "features.f3.body":
      "Connect your own OKX. AI opens positions on signal, exits at +5%. Total exposure ≤ 3% of balance — crashing won't blow you up.",
    "features.f4.title": "Price alerts · voice chat",
    "features.f4.body":
      "BTC drops below $77K → push notification. Hold-to-talk WeChat-style → AI transcribes → Claw replies. Your trading desk in your pocket.",

    "cta.title": "Take Claw with you",
    "cta.subtitle": "iOS (Expo Go) and Android APK are live — scan the QR to try it now.",
    "cta.button": "Get the App",

    "download.heading": "Get the btcmind app",
    "download.subtitle":
      "Your AI trading copilot in your pocket. Voice-chat with Claw, get daily prediction summaries, audit your portfolio anywhere.",
    "download.expo.badge": "Dev Preview — no install needed",
    "download.expo.title": "Scan to try it instantly",
    "download.expo.body":
      "iPhone users: install Expo Go from the App Store, then scan the QR with your camera to open btcmind.",
    "download.expo.linkPrefix": "Or open the link directly:",
    "download.altHeading": "Or grab the full install",
    "download.ios.subtitle": "iPhone & iPad — iOS 16+",
    "download.ios.primary": "Join TestFlight",
    "download.ios.primaryDisabled": "Coming soon",
    "download.ios.secondary": "Or scan via Expo Go (dev preview)",
    "download.ios.note":
      "TestFlight is the public beta channel. Install TestFlight on iPhone first, then tap the link.",
    "download.ios.noteFallback":
      "App Store / TestFlight build is rolling out. In the meantime, install Expo Go and scan the QR above.",
    "download.android.subtitle": "Android 8.0+ (Oreo and up)",
    "download.android.primary": "Download APK",
    "download.android.primaryDisabled": "Building…",
    "download.android.secondary": "Or install via Expo Go",
    "download.android.note":
      "After download, allow installs from your browser, then open the APK. We'll prompt you for camera + microphone.",
    "download.android.noteFallback":
      "First Android build is queued — refresh this page in a few minutes for a direct download link.",
    "download.steps.heading": "First-time setup",
    "download.steps.1": "Install via the buttons above, then open btcmind.",
    "download.steps.2":
      "Settings → Sign in. Enter your email and the invite code (admin emails skip the link). Magic link arrives instantly.",
    "download.steps.3":
      "Allow microphone access for voice input — hold-to-talk, WeChat-style.",
    "download.steps.4":
      "Toggle Daily Reminder in Settings to get a prediction summary at the time you pick.",
    "download.invite.text": "Need an invite code?",
    "download.invite.cta": "Request access on the homepage",

    "footer.tagline": "btcmind · Your AI trading copilot",
    "footer.copy": "© 2026 btcmind. Not investment advice.",
  },
  ja: {
    "brand.name": "btcmind",
    "nav.features": "機能",
    "nav.agents": "AI エージェント",
    "nav.pricing": "料金",
    "nav.download": "ダウンロード",
    "nav.telegram": "Telegram",
    "nav.discord": "Discord",
    "nav.login": "ログイン",
    "nav.getApp": "アプリ",

    "hero.badge": "ライブ運用中 · 6 体の AI が市場を解析中",
    "hero.title.line1": "AIが",
    "hero.title.highlight": "監視 · 判断 · 執行",
    "hero.subtitle":
      "「相場見」「分析」「発注」を一括で 6 体の AI 専門家へ。マルチエージェント議論 → 予測 → 自動約定 → +5% 自動利確。あなたは日次レポートを見るだけ。",
    "hero.cta.primary": "アプリを入手",
    "hero.cta.secondary": "1 分デモを見る",
    "hero.stats.agents": "AI エージェント",
    "hero.stats.dag": "3 層 DAG",
    "hero.stats.auto": "24 時間自動執行",

    "features.title": "btcmind を選ぶ理由",
    "features.sub": "ただの AI アシスタントじゃない。取引フロー全体を自動化。",
    "features.f1.title": "実行カード形式の回答",
    "features.f1.body":
      "Claw の各回答は 8 セクションの実行カード：結論 / 重要価格 / 構造 / 行動 / 無効化条件。「$77K を割れば半分減らす、$80K を超えれば買い増し」のように具体的。「気をつけて」のような決まり文句はなし。",
    "features.f2.title": "マルチエージェント議論 → 真の予測",
    "features.f2.body":
      "Bull / Bear リサーチャーが討論、テクニカル / デリバティブ / テールリスクが並列分析、ポートフォリオマネージャーが BUY/SELL/HOLD + 信頼度を出力。全判断はトレーサブル。",
    "features.f3.title": "+5% 自動利確 · 3% ポジション上限",
    "features.f3.body":
      "あなた自身の OKX を接続。AI がシグナルでエントリー、+5% で利確。最大エクスポージャーは残高の 3% 以下 — 想定外の動きでも吹き飛ばない。",
    "features.f4.title": "価格アラート · 音声対話",
    "features.f4.body":
      "BTC が $77K を割ったら即プッシュ通知。WeChat 式の長押し録音 → AI 文字起こし → Claw が返信。ポケットの中の取引デスク。",

    "cta.title": "Claw をポケットへ",
    "cta.subtitle": "iOS（Expo Go）と Android APK 公開中。QR を読んで今すぐ試せます。",
    "cta.button": "ダウンロード",

    "download.heading": "btcmind アプリをダウンロード",
    "download.subtitle":
      "AI 取引コパイロットをポケットに。音声で Claw と会話、毎日予測のサマリーを通知、ポートフォリオをいつでも監査。",
    "download.expo.badge": "Dev プレビュー · インストール不要",
    "download.expo.title": "QR を読んで今すぐ試す",
    "download.expo.body":
      "iPhone は App Store から Expo Go を入手し、カメラで左の QR を読み取ってください。",
    "download.expo.linkPrefix": "またはリンクを直接開く：",
    "download.altHeading": "またはフルインストール",
    "download.ios.subtitle": "iPhone & iPad — iOS 16 以上",
    "download.ios.primary": "TestFlight に参加",
    "download.ios.primaryDisabled": "近日公開",
    "download.ios.secondary": "Expo Go でスキャン（開発プレビュー）",
    "download.ios.note":
      "TestFlight は公開ベータチャネル。iPhone に TestFlight を入れてから上のボタンをタップ。",
    "download.ios.noteFallback":
      "App Store / TestFlight 版は近日公開。それまでは上の Expo Go QR で全機能を試せます。",
    "download.android.subtitle": "Android 8.0 以上 (Oreo 以降)",
    "download.android.primary": "APK をダウンロード",
    "download.android.primaryDisabled": "ビルド中…",
    "download.android.secondary": "Expo Go をインストール",
    "download.android.note":
      "ダウンロード後、ブラウザに「不明なソースからのインストール」を許可し、APK を開いてください。初回起動でカメラとマイクの権限を求めます。",
    "download.android.noteFallback":
      "初回ビルドはキュー待機中。数分後にこのページを再読込で直接リンクが出ます。",
    "download.steps.heading": "初回セットアップ",
    "download.steps.1": "上のボタンでインストールし、btcmind を起動。",
    "download.steps.2":
      "「設定」→「ログイン」へ。メールと招待コードを入力（管理者メールは直接ログイン）。マジックリンクが届きます。",
    "download.steps.3":
      "マイク権限を許可すると、チャット画面でボタン長押しで録音（WeChat 風、離して送信）。",
    "download.steps.4":
      "「設定」で毎日リマインダーをオンにすると、お好きな時刻に予測サマリーが届きます。",
    "download.invite.text": "招待コードが必要？",
    "download.invite.cta": "トップページから申請",

    "footer.tagline": "btcmind · あなたの AI 取引コパイロット",
    "footer.copy": "© 2026 btcmind. 投資助言ではありません。",
  },
};

export function t(locale: Locale, key: string): string {
  return messages[locale]?.[key] ?? messages[DEFAULT_LOCALE][key] ?? key;
}
