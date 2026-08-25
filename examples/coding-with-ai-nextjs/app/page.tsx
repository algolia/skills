import { Providers } from "./providers";
import { Search } from "./components/Search";
import { ChatWidget } from "./components/ChatWidget";

// Server Component. It composes the client provider and client UI — a Server
// Component may render Client Components, but the Algolia/chat pieces themselves
// must be Client Components ("use client"), because the streaming Chat widget and
// InstantSearch hooks are browser-only.
export default function Home() {
  return (
    <Providers>
      <main className="page">
        <header className="page-header">
          <h1>Coding with AI</h1>
          <p>Algolia search plus an Agent Studio shopping assistant.</p>
        </header>
        <Search />
      </main>
      {/* The floating chat widget renders its own toggle button. */}
      <ChatWidget />
    </Providers>
  );
}
