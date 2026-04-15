# Autocomplete Styling

This covers autocomplete-specific styling. For the general approach, see the [styling guide](../styling.md).

## Desktop: Dropdown Panel

On desktop, the autocomplete panel appears as a dropdown below the search input. Ensure:

- The panel is positioned relative to the input (the widget handles this by default)
- The panel has a background, border/shadow, and appropriate width
- The panel doesn't overflow the viewport. Set a `max-height` and `overflow-y: auto`

## Mobile: Detached Full-Viewport Overlay

Set the `detachedMediaQuery` prop to match the project's mobile breakpoint (inspect the CSS config to find it).

The widget does not style the detached overlay as a full-viewport takeover out of the box. You must apply the following CSS structure (adapt values to the project's styling approach, but the layout properties are mandatory):

```css
/* 1. Lock the body to prevent scroll behind the overlay */
body.ais-Autocomplete--detached {
  height: 100vh;
  overflow: hidden;
  position: fixed;
  width: 100%;
}

/* 2. Semi-transparent backdrop behind the container */
.ais-AutocompleteDetachedOverlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 100vh;
  z-index: 9998;
}

/* 3. Full-screen container, flex column so the panel fills remaining space */
.ais-AutocompleteDetachedContainer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 9999;
}

/* 4. Form area at the top, does not grow */
.ais-AutocompleteDetachedFormContainer {
  display: flex;
  flex-direction: row;
  flex-shrink: 0;
}

/* 5. Panel fills remaining space via flex-grow */
.ais-AutocompleteDetachedContainer .ais-AutocompletePanel {
  flex-grow: 1;
  position: relative;
  overflow: hidden;
  top: 0;
}

/* 6. Inner panel layout scrolls within the flex-grown space */
.ais-AutocompleteDetachedContainer .ais-AutocompletePanelLayout {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
}
```

All six selectors are required. The key insight is that the **panel uses `flex-grow: 1` + `position: relative`**, and the **inner panel layout uses `position: absolute` with inset 0** to fill the flex-grown space and scroll. Do not set the panel itself to `position: fixed`. That breaks the flex layout.

Verify by testing at a mobile breakpoint. Broken positioning is not visible at desktop widths.

## Item Styling

Autocomplete items (products, suggestions, recent searches) share common wrapper classes that carry layout responsibility. When grepping for `ais-` class names, pay attention to the DOM nesting. The outermost shared classes need layout styles (display, alignment, padding), while type-specific classes nested inside them only need type-specific overrides. Inspect the rendered HTML or grep the source to understand the hierarchy before styling.

## Query Suggestion Highlighting

Query suggestions use `ReverseHighlight` internally: instead of highlighting the matching text, they highlight the completion (the part the user hasn't typed yet). The highlighted portion is rendered inside a `<mark>` element with the class `ais-ReverseHighlight-highlighted`.

Style it to make completions bold and reset the default `<mark>` background:

```css
.ais-ReverseHighlight-highlighted {
  font-weight: bold;
  background: none;
}
```

Without this, suggestions appear as plain unstyled text with no distinction between what the user typed and what's being suggested.

## Interaction States

All interactive items (product results, query suggestions, recent searches) must have hover states that match their keyboard-selected states. Users interact with both pointer and keyboard. The visual feedback must be consistent across both.

Style `:hover` and active/selected states on all item types.

## Search Input

The autocomplete replaces whatever search input existed before. Make sure:

- The new input matches the site's design (colors, border radius, padding, placeholder text style)
- If the original input was hidden on certain breakpoints (e.g., `hidden sm:block`), remove that restriction. The autocomplete trigger must be visible at all screen sizes, especially mobile where detached mode needs it
