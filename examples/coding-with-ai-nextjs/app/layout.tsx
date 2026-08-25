import type { Metadata } from "next";
import "./globals.css";

// Root layout is a Server Component. Global CSS is imported here (the App Router
// convention). Client-side Algolia/chat UI is composed inside the page.
export const metadata: Metadata = {
  title: "Coding with AI — Algolia reference app",
  description: "Algolia InstantSearch + an Agent Studio chat agent on the Next.js App Router.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
