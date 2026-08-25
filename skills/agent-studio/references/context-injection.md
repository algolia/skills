# Context Injection — Full Implementation

## ChatContext Provider

```tsx
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

interface ChatState {
  chatIsOpen: boolean;
  pendingMessage: string | null;
  pendingContextMessage: string | null;
  requestOpen: () => void;
  requestClose: () => void;
  requestOpenWithMessage: (message: string) => void;
  consumePendingMessage: () => string | null;
  sendWithContext: (context: string, visibleMessage?: string) => void;
  consumePendingContextMessage: () => void;
}

const ChatContext = createContext<ChatState | null>(null);

export function useChatActions() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChatActions must be inside ChatProvider");
  return ctx;
}

function isChatOpen(): boolean {
  return !!document.querySelector(".ais-Chat-container--open");
}

function clickChatToggle() {
  const btn = document.querySelector<HTMLButtonElement>(".ais-ChatToggleButton");
  btn?.click();
}

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [chatIsOpen, setChatIsOpen] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [pendingContextMessage, setPendingContextMessage] = useState<string | null>(null);

  // Poll DOM for open/close state
  useEffect(() => {
    const interval = setInterval(() => setChatIsOpen(isChatOpen()), 150);
    return () => clearInterval(interval);
  }, []);

  const requestOpen = useCallback(() => {
    if (!isChatOpen()) clickChatToggle();
  }, []);

  const requestClose = useCallback(() => {
    if (isChatOpen()) clickChatToggle();
  }, []);

  const requestOpenWithMessage = useCallback((msg: string) => {
    setPendingMessage(msg);
    if (!isChatOpen()) clickChatToggle();
  }, []);

  const consumePendingMessage = useCallback(() => {
    const msg = pendingMessage;
    setPendingMessage(null);
    return msg;
  }, [pendingMessage]);

  const sendWithContext = useCallback(
    (context: string, visibleMessage?: string) => {
      const fullText = `[Context: ${context}]${visibleMessage || ""}`;

      function injectAndSubmit() {
        const textarea = document.querySelector<HTMLTextAreaElement>(
          ".ais-ChatPrompt textarea, .ais-Chat textarea"
        );
        if (!textarea) return false;

        // Set via native setter to trigger React's onChange
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
          window.HTMLTextAreaElement.prototype,
          "value"
        )?.set;
        nativeInputValueSetter?.call(textarea, fullText);
        textarea.dispatchEvent(new Event("input", { bubbles: true }));

        // Submit after React processes input
        setTimeout(() => {
          const form = textarea.closest("form");
          if (form) {
            form.dispatchEvent(
              new Event("submit", { bubbles: true, cancelable: true })
            );
          }
        }, 50);
        return true;
      }

      if (isChatOpen()) {
        if (!injectAndSubmit()) {
          let attempts = 0;
          const retry = setInterval(() => {
            if (injectAndSubmit() || ++attempts > 10) clearInterval(retry);
          }, 100);
        }
      } else {
        setPendingContextMessage(fullText);
        setTimeout(clickChatToggle, 50);
      }
    },
    []
  );

  const consumePendingContextMessage = useCallback(() => {
    setPendingContextMessage(null);
  }, []);

  return (
    <ChatContext.Provider
      value={{
        chatIsOpen,
        pendingMessage,
        pendingContextMessage,
        requestOpen,
        requestClose,
        requestOpenWithMessage,
        consumePendingMessage,
        sendWithContext,
        consumePendingContextMessage,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}
```

## Context Stripping Hook

```tsx
import { useEffect } from "react";

const CONTEXT_PATTERN = /^\[Context:\s*([\s\S]*?)\]([\s\S]*)$/;
const PROCESSED_ATTR = "data-ctx-stripped";

export function useContextStripping() {
  useEffect(() => {
    function processUserMessage(el: Element) {
      if (el.hasAttribute(PROCESSED_ATTR)) return;

      const messageEl = el.querySelector(".ais-ChatMessage-message");
      if (!messageEl) return;

      const text = messageEl.textContent || "";
      const match = text.match(CONTEXT_PATTERN);
      if (!match) return;

      el.setAttribute(PROCESSED_ATTR, "true");
      const visibleText = match[2].trim();

      if (!visibleText) {
        // Context-only message: hide entirely
        (el as HTMLElement).style.display = "none";
      } else {
        // Context + visible text: show only visible portion
        messageEl.textContent = visibleText;
      }
    }

    function scanAll() {
      document
        .querySelectorAll(`.ais-ChatMessage--right:not([${PROCESSED_ATTR}])`)
        .forEach(processUserMessage);
    }

    // Use both MutationObserver and polling for reliability
    const container = document.querySelector(".ais-Chat") || document.body;
    const observer = new MutationObserver(() => scanAll());
    observer.observe(container, {
      childList: true,
      subtree: true,
      characterData: true,
    });

    const poll = setInterval(scanAll, 300);
    scanAll();

    return () => {
      observer.disconnect();
      clearInterval(poll);
    };
  }, []);
}
```

Call `useContextStripping()` inside your chat wrapper component (the one that renders `<Chat>`).

## Provider Hierarchy

```tsx
<BrowserRouter>
  <AuthProvider>
    <CartProvider>
      <ChatProvider>
        <App />
      </ChatProvider>
    </CartProvider>
  </AuthProvider>
</BrowserRouter>
```

ChatProvider must wrap any component that calls `useChatActions()`.

## Usage: Auto-inject context on product pages

```tsx
function ProductPage() {
  const { chatIsOpen, sendWithContext } = useChatActions();
  const product = useProduct();
  const hasEngagedRef = useRef(false);

  useEffect(() => {
    if (!chatIsOpen || !product || hasEngagedRef.current) return;
    hasEngagedRef.current = true;

    const ctx = [
      `User is browsing "${product.name}" (ID: ${product.objectID}).`,
      `Price: $${product.price.toFixed(2)}.`,
      product.brand ? `Brand: ${product.brand}.` : "",
      product.category ? `Category: ${product.category}.` : "",
      product.description ? `Description: ${product.description}` : "",
      `Help the user with this product.`,
    ].filter(Boolean).join(" ");

    sendWithContext(ctx); // No visible message — context only, hidden from user
  }, [chatIsOpen, product, sendWithContext]);
}
```
