import { NextResponse } from "next/server";
import jwt from "jsonwebtoken";

// jsonwebtoken relies on Node crypto, so this handler must run on the Node.js
// runtime (not the Edge runtime).
export const runtime = "nodejs";

// POST /api/auth/algolia-token
//
// Mints a short-lived HS256 JWT that scopes Agent Studio memory & conversations
// to a user. The secret is read from a server-only env var and NEVER leaves the
// server — the browser only ever receives the signed token.
//
// Get ALGOLIA_SECRET_KEY (sk-alg-...) and ALGOLIA_KEY_ID from Agent Studio:
// Settings > Authentication.
export async function POST(request: Request) {
  const secret = process.env.ALGOLIA_SECRET_KEY;
  const keyId = process.env.ALGOLIA_KEY_ID;

  if (!secret || !keyId) {
    return NextResponse.json(
      { error: "Server is not configured with ALGOLIA_SECRET_KEY / ALGOLIA_KEY_ID" },
      { status: 500 }
    );
  }

  // In a real app, derive the user ID from the authenticated session — do NOT
  // trust a client-supplied ID. This demo reads it from the request body.
  let userId = "anonymous";
  try {
    const body = (await request.json()) as { userId?: unknown };
    if (typeof body?.userId === "string" && body.userId.length > 0) {
      userId = body.userId;
    }
  } catch {
    // No/invalid body → treat as anonymous.
  }

  const token = jwt.sign({ sub: userId }, secret, {
    expiresIn: "24h",
    header: {
      alg: "HS256",
      typ: "JWT",
      kid: keyId, // Key ID from Agent Studio Settings > Authentication
    },
  });

  return NextResponse.json({ token });
}
