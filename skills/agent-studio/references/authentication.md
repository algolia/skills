# User Authentication & Secure Tokens — Full Reference

Memory and conversation scoping require user authentication via JWT tokens. The
token is minted server-side (so the Agent Studio secret never reaches the
browser) and passed to the Chat transport as the
`X-Algolia-Secure-User-Token` header.

## Server-side token generation

The secret (`sk-alg-...`) and key ID come from Agent Studio
**Settings > Authentication**. Sign an HS256 JWT whose `sub` is the user's ID
and whose header carries the `kid`.

```typescript
import jwt from "jsonwebtoken";

// Endpoint: POST /api/auth/algolia-token
const token = jwt.sign(
  { sub: userId },
  process.env.ALGOLIA_SECRET_KEY, // sk-alg-... from Agent Studio Settings
  {
    expiresIn: "24h",
    header: {
      alg: "HS256",
      typ: "JWT",
      kid: process.env.ALGOLIA_KEY_ID, // Key ID from the same page
    },
  }
);
```

## Client-side token management

Cache the token and refresh it before it expires (decode the `exp` claim). Fall
back to `null` for anonymous users so the Chat still works without memory.

```typescript
let cachedToken: { token: string; expiresAt: number } | null = null;

async function fetchAlgoliaToken(): Promise<string | null> {
  // Return cached token if it is not expiring within the next 5 minutes
  if (cachedToken && cachedToken.expiresAt > Date.now() + 5 * 60 * 1000) {
    return cachedToken.token;
  }
  try {
    const { token } = await apiClient("/auth/algolia-token", { method: "POST" });
    const payload = JSON.parse(atob(token.split(".")[1]));
    cachedToken = { token, expiresAt: payload.exp * 1000 };
    return token;
  } catch {
    return null;
  }
}
```

Pass the token in the Chat transport headers as `X-Algolia-Secure-User-Token`
(see the "Custom transport" section of SKILL.md).

## Account switching / logout

When a user logs out or switches accounts, clear the chat session storage so
old conversations don't persist:

```typescript
const prefix = "instantsearch-chat-initial-messages";
for (let i = sessionStorage.length - 1; i >= 0; i--) {
  const key = sessionStorage.key(i);
  if (key?.startsWith(prefix)) sessionStorage.removeItem(key);
}
```

Also re-key the `<InstantSearch>` component on user change so React remounts the
chat with a fresh session: `key={user?.id ?? "anon"}`.
