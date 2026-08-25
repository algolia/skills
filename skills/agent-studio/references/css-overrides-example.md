# CSS Overrides Example — Monochrome Design System

This is a complete example of overriding the default Algolia Chat styles to match a monochrome/minimal design system. Use it as a starting template and adapt colors, fonts, and spacing to your brand.

## Full CSS File

```css
/* Chat widget — Custom overrides */
/* Layered on top of instantsearch.css/components/chat.css */

/* ========== Design system token overrides ========== */
.ais-Chat {
  --ais-primary-color-rgb: 0, 0, 0;            /* primary color as RGB */
  --ais-primary-color-alpha: 1;
  --ais-text-color-rgb: 26, 28, 29;             /* main text */
  --ais-muted-color-rgb: 71, 71, 71;            /* secondary text */
  --ais-background-color-rgb: 255, 255, 255;    /* background */
  --ais-background-color-alpha: 1;
  --ais-border-color-rgb: 198, 198, 198;        /* borders */
  --ais-border-color-alpha: 0.25;
  --ais-chat-margin: 1.5rem;
  --ais-font-family: "Inter", system-ui, sans-serif;
  font-family: "Inter", system-ui, sans-serif;
}

/* Force font everywhere inside chat */
.ais-Chat,
.ais-Chat *,
.ais-Chat *::before,
.ais-Chat *::after {
  font-family: "Inter", system-ui, sans-serif !important;
}

/* ========== Typography ========== */
.ais-ChatHeader-title {
  font-weight: 700 !important;
  font-size: 0.9375rem !important;
  letter-spacing: -0.02em !important;
  color: #1a1c1d !important;
}

.ais-ChatMessage-message {
  font-size: 0.875rem !important;
  line-height: 1.55 !important;
  letter-spacing: -0.006em !important;
  color: #474747 !important;
}

.ais-ChatMessage--user .ais-ChatMessage-message {
  color: #f0f0f2 !important;
}

.ais-ChatMessage-message strong,
.ais-ChatMessage-message b {
  font-weight: 600 !important;
  color: #1a1c1d !important;
}

.ais-ChatMessage--user .ais-ChatMessage-message strong,
.ais-ChatMessage--user .ais-ChatMessage-message b {
  color: #ffffff !important;
}

/* Kill any remaining default blue on focus/active states */
.ais-Chat *:focus,
.ais-Chat *:focus-visible {
  outline-color: #000000 !important;
  border-color: #000000 !important;
  box-shadow: none !important;
}

.ais-Chat *::selection {
  background: rgba(0, 0, 0, 0.12) !important;
  color: inherit !important;
}

/* ========== Mobile: position above bottom nav ========== */
@media (max-width: 680px) {
  .ais-Chat {
    inset: auto 0 4rem 0 !important;  /* 4rem = bottom nav height */
    height: auto !important;
    max-height: calc(85vh - 4rem) !important;
    width: 100% !important;
    max-width: 100% !important;
  }
}

/* ========== Toggle button ========== */
.ais-ChatToggleButton {
  border-radius: 9999px !important;
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(24px) !important;
  -webkit-backdrop-filter: blur(24px) !important;
  box-shadow: 0px 20px 40px rgba(26, 28, 29, 0.06) !important;
  border: 1px solid rgba(198, 198, 198, 0.3) !important;
  width: 3.5rem !important;
  height: 3.5rem !important;
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}

.ais-ChatToggleButton:hover {
  transform: scale(1.08) !important;
}

.ais-ChatToggleButton:active {
  transform: scale(0.95) !important;
}

/* Mobile: hide floating toggle when using bottom nav */
@media (max-width: 680px) {
  .ais-ChatToggleButton {
    display: none !important;
  }
}

/* ========== Panel container ========== */
.ais-Chat-container {
  background: #ffffff !important;
  font-family: "Inter", system-ui, sans-serif !important;
  border: 1px solid rgba(198, 198, 198, 0.15) !important;
}

/* Desktop: floating card */
@media (min-width: 681px) {
  .ais-Chat-container {
    border-radius: 1rem !important;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.08),
                0 8px 20px rgba(0, 0, 0, 0.04) !important;
  }

  @media (prefers-reduced-motion: no-preference) {
    .ais-Chat-container {
      transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                  transform 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .ais-Chat-container.ais-Chat-container--open {
      transition: opacity 0.35s cubic-bezier(0, 0, 0.2, 1),
                  transform 0.45s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
  }
}

/* Mobile: bottom sheet with slide-up */
@media (max-width: 680px) {
  .ais-Chat-container {
    border-radius: 1.5rem 1.5rem 0 0 !important;
    border-bottom: none !important;
    box-shadow: 0 -8px 50px rgba(0, 0, 0, 0.1),
                0 -2px 15px rgba(0, 0, 0, 0.05) !important;
    max-height: 85vh !important;
  }

  .ais-Chat-container {
    transform: translateY(105%) !important;
    opacity: 0 !important;
    transition: transform 0.55s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.4s cubic-bezier(0.4, 0, 1, 1) !important;
  }

  .ais-Chat-container.ais-Chat-container--open {
    transform: translateY(0) !important;
    opacity: 1 !important;
    transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1),
                opacity 0.3s cubic-bezier(0, 0, 0.2, 1) !important;
  }

  /* Drag handle */
  .ais-Chat-container::before {
    content: "" !important;
    display: block !important;
    width: 2.25rem !important;
    height: 0.25rem !important;
    background: rgba(0, 0, 0, 0.12) !important;
    border-radius: 9999px !important;
    margin: 0.625rem auto 0.25rem !important;
    flex-shrink: 0 !important;
  }
}

/* ========== Header ========== */
.ais-ChatHeader {
  background: #ffffff !important;
  border-bottom: none !important;
  color: #1a1c1d !important;
}

.ais-ChatHeader-clear,
.ais-ChatHeader-close,
.ais-ChatHeader-minimize,
.ais-ChatHeader-maximize {
  color: #474747 !important;
}

.ais-ChatHeader-clear:hover,
.ais-ChatHeader-close:hover {
  color: #1a1c1d !important;
}

/* ========== Messages ========== */
.ais-ChatMessages {
  background: #ffffff !important;
}

.ais-ChatMessage {
  animation: chatMsgIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) both !important;
}

@keyframes chatMsgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* User bubble */
.ais-ChatMessage--user .ais-ChatMessage-message {
  background: #1a1c1d !important;
  color: #f0f0f2 !important;
  border-color: transparent !important;
}

/* Assistant bubble */
.ais-ChatMessage--assistant .ais-ChatMessage-message {
  background: #f3f3f5 !important;
  color: #1a1c1d !important;
  border-color: transparent !important;
}

/* Action icons */
.ais-ChatMessage-actions button,
.ais-ChatMessage-actions svg {
  color: #777777 !important;
}

.ais-ChatMessage-actions button:hover,
.ais-ChatMessage-actions button:hover svg {
  color: #1a1c1d !important;
}

/* ========== Product carousel ========== */
.ais-ChatMessage-message .ais-ChatToolSearchIndexCarousel-list,
.ais-ChatMessage-message .ais-Recommend-list {
  display: flex !important;
  gap: 0.75rem !important;
  overflow-x: auto !important;
  padding: 0.25rem 0.25rem 0.5rem !important;
  scrollbar-width: none !important;
  scroll-snap-type: x mandatory !important;
  -webkit-overflow-scrolling: touch !important;
}

.ais-ChatMessage-message .ais-ChatToolSearchIndexCarousel-list::-webkit-scrollbar,
.ais-ChatMessage-message .ais-Recommend-list::-webkit-scrollbar {
  display: none !important;
}

.ais-ChatMessage-message .ais-ChatToolSearchIndexCarousel-item,
.ais-ChatMessage-message .ais-Recommend-item {
  flex-shrink: 0 !important;
  width: 10rem !important;
  list-style: none !important;
  scroll-snap-align: start !important;
}

/* Links */
.ais-ChatToolSearchIndexCarouselHeaderResults a,
.ais-ChatMessage-message a {
  color: #1a1c1d !important;
  text-decoration: underline !important;
  text-underline-offset: 2px !important;
}

.ais-ChatMessage-message a:hover {
  text-decoration: none !important;
}

/* ========== Prompt area ========== */
.ais-ChatPrompt {
  background: #ffffff !important;
  border-top: 1px solid rgba(198, 198, 198, 0.12) !important;
  padding: 0.5rem !important;
  padding-bottom: calc(0.5rem + env(safe-area-inset-bottom, 0px)) !important;
}

.ais-ChatPrompt .ais-ChatPrompt-textarea {
  font-size: 0.875rem !important;
  color: #1a1c1d !important;
  border-color: rgba(198, 198, 198, 0.3) !important;
  caret-color: #000000 !important;
  min-height: 0 !important;
  max-height: 5rem !important;
  padding: 0.5rem 0.625rem !important;
}

.ais-ChatPrompt .ais-ChatPrompt-textarea::placeholder {
  color: #777777 !important;
}

.ais-ChatPrompt .ais-ChatPrompt-textarea:focus {
  border-color: #000000 !important;
  outline: none !important;
  box-shadow: none !important;
}

/* Submit button */
.ais-ChatPrompt-submit {
  background: #000000 !important;
  color: #e5e2e1 !important;
  border-radius: 0.25rem !important;
  border: none !important;
  transition: opacity 0.2s ease !important;
}

.ais-ChatPrompt-submit:hover {
  opacity: 0.85 !important;
}

.ais-ChatPrompt-submit svg {
  color: #e5e2e1 !important;
  fill: #e5e2e1 !important;
}

/* Footer text */
.ais-ChatPrompt-footer {
  color: #777777 !important;
}

/* ========== Suggestions ========== */
.ais-ChatPromptSuggestions-suggestion {
  border: 1px solid rgba(198, 198, 198, 0.4) !important;
  border-radius: 0.75rem !important;
  font-size: 0.8125rem !important;
  color: #474747 !important;
  transition: background 0.2s ease, border-color 0.2s ease !important;
}

.ais-ChatPromptSuggestions-suggestion:hover {
  background: #f3f3f5 !important;
  border-color: rgba(198, 198, 198, 0.6) !important;
  color: #1a1c1d !important;
}

/* ========== Loading indicator ========== */
.ais-ChatMessages-loader {
  color: #474747 !important;
}

/* ========== Desktop scrollbar ========== */
@media (min-width: 681px) {
  .ais-ChatMessages-scroll::-webkit-scrollbar {
    width: 4px;
  }
  .ais-ChatMessages-scroll::-webkit-scrollbar-track {
    background: transparent;
  }
  .ais-ChatMessages-scroll::-webkit-scrollbar-thumb {
    background: rgba(198, 198, 198, 0.4);
    border-radius: 9999px;
  }
}
```

## Adapting to Other Brand Colors

To adapt this to a different brand, change these key values:

1. `--ais-primary-color-rgb` — your primary brand color as R, G, B
2. `.ais-ChatMessage--user .ais-ChatMessage-message background` — user bubble color
3. `.ais-ChatPrompt-submit background` — submit button color
4. Focus/selection colors — match your primary
5. Font family — replace "Inter" with your brand font
