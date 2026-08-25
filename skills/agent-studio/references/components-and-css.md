# Custom Components & CSS — Full Reference

## Item component (product cards in chat)

The item component receives Algolia hit objects. Field names depend on your
index schema. Common fields: `objectID`, `name`/`title`, `price`, `image`,
`brand`, `category`.

```tsx
<Chat
  itemComponent={({ item }) => (
    <Link
      to={`/product/${item.objectID}`}
      className="block w-40 shrink-0 rounded-xl overflow-hidden"
    >
      <img src={item.image} alt={item.name} className="w-full aspect-square object-cover" />
      <div className="p-2">
        <p className="text-sm font-bold truncate">{item.name}</p>
        <span className="text-sm">${item.price}</span>
      </div>
    </Link>
  )}
/>
```

## Suggestions component

Use the built-in CSS class names (`ais-ChatPromptSuggestions`,
`ais-ChatPromptSuggestions-suggestion`) so the default styles and your
overrides apply.

```tsx
<Chat
  suggestionsComponent={({ suggestions = [], onSuggestionClick }) => {
    if (suggestions.length === 0) return <></>;
    return (
      <div className="ais-ChatPromptSuggestions">
        {suggestions.map((s) => (
          <button
            key={s}
            className="ais-ChatPromptSuggestions-suggestion"
            type="button"
            onClick={() => onSuggestionClick(s)}
          >
            {s}
          </button>
        ))}
      </div>
    );
  }}
/>
```

## Other customizable components

The Chat component accepts these additional component props:

- `headerCloseIconComponent`, `headerMaximizeIconComponent`,
  `headerMinimizeIconComponent`, `headerTitleIconComponent`
- `messagesErrorComponent`, `messagesLoaderComponent`
- `messageAssistantLeadingComponent`, `messageAssistantFooterComponent`
- `messageUserLeadingComponent`, `messageUserFooterComponent`
- `promptFooterComponent`, `promptHeaderComponent`
- `toggleButtonIconComponent`

## Translations

```tsx
<Chat
  translations={{
    prompt: {
      textareaPlaceholder: "Ask me anything about our products...",
      disclaimer: "AI-powered assistant. Responses may not be perfect.",
      sendMessageTooltip: "Send",
    },
    header: {
      title: "Shopping Assistant",
    },
  }}
/>
```

## Design tokens (CSS custom properties)

Set these on `.ais-Chat` to rebrand the widget:

```css
.ais-Chat {
  --ais-primary-color-rgb: 0, 0, 0;          /* Primary brand color (RGB) */
  --ais-primary-color-alpha: 1;
  --ais-text-color-rgb: 26, 28, 29;           /* Main text */
  --ais-muted-color-rgb: 71, 71, 71;          /* Secondary text */
  --ais-background-color-rgb: 255, 255, 255;  /* Background */
  --ais-background-color-alpha: 1;
  --ais-border-color-rgb: 198, 198, 198;      /* Borders */
  --ais-border-color-alpha: 0.25;
  --ais-chat-margin: 1.5rem;                  /* Outer margin */
  --ais-font-family: "Inter", system-ui, sans-serif;
}
```

## Key CSS class names

| Element | Class | Notes |
|---------|-------|-------|
| Root | `.ais-Chat` | Top-level container |
| Panel | `.ais-Chat-container` | The chat panel |
| Panel open | `.ais-Chat-container--open` | When chat is visible |
| Toggle button | `.ais-ChatToggleButton` | Floating open/close button |
| Header | `.ais-ChatHeader` | Title bar |
| Header title | `.ais-ChatHeader-title` | Title text |
| Messages area | `.ais-ChatMessages` | Scrollable message list |
| Message | `.ais-ChatMessage` | Individual message |
| User message | `.ais-ChatMessage--user` | User's messages |
| Assistant message | `.ais-ChatMessage--assistant` | Agent's messages |
| Message bubble | `.ais-ChatMessage-message` | The bubble itself |
| Actions | `.ais-ChatMessage-actions` | Copy/regenerate buttons |
| Prompt area | `.ais-ChatPrompt` | Input section |
| Textarea | `.ais-ChatPrompt-textarea` | Input field |
| Submit button | `.ais-ChatPrompt-submit` | Send button |
| Suggestions | `.ais-ChatPromptSuggestions-suggestion` | Suggestion chips |
| Product carousel | `.ais-ChatToolSearchIndexCarousel-list` | Product list container |
| Product item | `.ais-ChatToolSearchIndexCarousel-item` | Individual product card |
| Carousel header | `.ais-ChatToolSearchIndexCarouselHeader-title` | Section title above carousel |
| Loader | `.ais-ChatMessages-loader` | Typing indicator |

## Common customization patterns

**Mobile bottom-sheet pattern** — position the chat above a mobile bottom nav
and style it as a slide-up sheet:

```css
@media (max-width: 680px) {
  .ais-Chat {
    inset: auto 0 4rem 0 !important;  /* 4rem = bottom nav height */
    max-height: calc(85vh - 4rem) !important;
  }
  .ais-Chat-container {
    border-radius: 1.5rem 1.5rem 0 0 !important;
  }
  .ais-ChatToggleButton {
    display: none !important; /* Use your own nav button instead */
  }
}
```

**Product carousel styling:**

```css
.ais-ChatMessage-message .ais-ChatToolSearchIndexCarousel-list {
  display: flex !important;
  gap: 0.75rem !important;
  overflow-x: auto !important;
  scroll-snap-type: x mandatory !important;
  scrollbar-width: none !important;
}
.ais-ChatToolSearchIndexCarousel-item {
  flex-shrink: 0 !important;
  width: 10rem !important;
  scroll-snap-align: start !important;
}
```

For a complete CSS override file (monochrome design system), see
`css-overrides-example.md`.
