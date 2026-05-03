/**
 * Magic-link landing on the web. The link
 *   https://btcmind.ai/auth/verify?token=<token>
 * arrives here.
 *
 * On iOS/Android with the app installed, the OS intercepts the URL via
 * universal links / app links and opens the mobile app's
 * /(auth)/verify-email route directly — this page is the fallback for
 * desktop browsers and devices without the app installed. We just call
 * the API, surface success/failure, and prompt to install the app.
 */
'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

function VerifyInner() {
  const params = useSearchParams();
  const token = params.get('token');
  const [state, setState] = useState<'pending' | 'ok' | 'err'>('pending');
  const [errMsg, setErrMsg] = useState('');

  useEffect(() => {
    if (!token) {
      setState('err');
      setErrMsg('Missing token');
      return;
    }
    fetch(`${API_BASE}/v1/auth/email/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
      .then(async (r) => {
        if (r.ok) setState('ok');
        else {
          const j = await r.json().catch(() => ({}));
          setErrMsg(j.detail || `HTTP ${r.status}`);
          setState('err');
        }
      })
      .catch((e) => {
        setErrMsg(e.message);
        setState('err');
      });
  }, [token]);

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-md text-center space-y-4">
        {state === 'pending' && <p className="text-zinc-400">Verifying your sign-in link…</p>}
        {state === 'ok' && (
          <>
            <h1 className="text-2xl font-bold text-cyan-400">You&apos;re signed in</h1>
            <p className="text-zinc-400">
              Open the btcmind app on your phone to continue. If you don&apos;t have it yet:
            </p>
            <div className="flex gap-3 justify-center">
              <a className="px-4 py-2 rounded-lg bg-cyan-400 text-black font-semibold" href="https://apps.apple.com/app/btcmind/id0">
                App Store
              </a>
              <a className="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-100 font-semibold" href="https://play.google.com/store/apps/details?id=ai.btcmind.app">
                Google Play
              </a>
            </div>
          </>
        )}
        {state === 'err' && (
          <>
            <h1 className="text-2xl font-bold text-red-400">Sign-in failed</h1>
            <p className="text-zinc-400">{errMsg}</p>
            <p className="text-zinc-500 text-sm">Open the app and request a new sign-in link.</p>
          </>
        )}
      </div>
    </main>
  );
}

export default function Verify() {
  return (
    <Suspense fallback={<main className="min-h-screen" />}>
      <VerifyInner />
    </Suspense>
  );
}
