/**
 * Privacy stub. Replace with legal-reviewed content before App Store submit.
 * Apple requires a privacy policy URL on the App Store Connect record.
 */
export const metadata = { title: 'Privacy Policy — btcmind' };

export default function Privacy() {
  return (
    <main className="max-w-2xl mx-auto px-6 py-16 prose prose-invert">
      <h1>Privacy Policy</h1>
      <p className="text-zinc-400">
        <em>Draft, last updated 2026-04-25. This page is a placeholder. The
        published policy must be reviewed by counsel before any public app
        release.</em>
      </p>

      <h2>1. What we collect</h2>
      <p>btcmind collects:</p>
      <ul>
        <li><strong>Account identifiers</strong>: your email address (and Apple/Google `sub` if you sign in with those).</li>
        <li><strong>Exchange credentials</strong>: OKX API key, secret, and passphrase, encrypted at rest with Fernet (AES-128 CBC + HMAC-SHA256).</li>
        <li><strong>Trading data</strong>: balances, orders, and trades retrieved from your OKX account through your provided API keys.</li>
        <li><strong>Operational logs</strong>: command logs and analysis runs for diagnostics.</li>
      </ul>

      <h2>2. How we use it</h2>
      <p>To execute the multi-agent analysis you request, manage grid/DCA strategies on your behalf, and surface portfolio/trade history in the app. We do not sell, share, or use your data for advertising.</p>

      <h2>3. Where it lives</h2>
      <p>Data is stored on managed infrastructure (Railway). OKX credentials never leave the encrypted SQLite store except briefly in memory during exchange calls.</p>

      <h2>4. Your rights</h2>
      <p>Email <a href="mailto:privacy@btcmind.ai">privacy@btcmind.ai</a> to delete your account and all associated data, or to export it.</p>

      <h2>5. Children</h2>
      <p>btcmind is not directed to anyone under 18.</p>
    </main>
  );
}
