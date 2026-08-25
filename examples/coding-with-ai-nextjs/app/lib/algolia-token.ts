"use client";

// Client-side helper: fetches the secure user token from our own Route Handler
// (app/api/auth/algolia-token/route.ts) and caches it until shortly before it
// expires. The Agent Studio secret NEVER reaches the browser — only the minted
// JWT does. Returns null for anonymous users so the chat still works without
// memory/personalization.

let cachedToken: { token: string; expiresAt: number } | null = null;

// Stub: a real app derives this from its own auth/session. Swap for the signed-in
// user's stable ID; use null (skip the fetch) for anonymous visitors.
const DEMO_USER_ID = "demo-user-123";

export async function fetchAlgoliaToken(): Promise<string | null> {
  // Reuse the cached token unless it expires within the next 5 minutes.
  if (cachedToken && cachedToken.expiresAt > Date.now() + 5 * 60 * 1000) {
    return cachedToken.token;
  }

  try {
    const res = await fetch("/api/auth/algolia-token", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ userId: DEMO_USER_ID }),
    });
    if (!res.ok) return null;

    const { token } = (await res.json()) as { token: string };
    const payload = JSON.parse(atob(token.split(".")[1])) as { exp: number };
    cachedToken = { token, expiresAt: payload.exp * 1000 };
    return token;
  } catch {
    // Anonymous fallback: chat works, just without user-scoped memory.
    return null;
  }
}
