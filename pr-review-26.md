<!-- type: pr-review -->
## PR Review

### Blocking

- `skills/algolia-migration/references/dart.md:1` — File should be removed: Dart is a new client with no legacy version to migrate from; a migration skill should not document it. *(raised by @Fluf22 — unresolved)*

- `skills/algolia-migration/references/go.md:20` (and ~270 instances across all 9 remaining reference files) — Code fence language identifiers contain doc-site rendering decorators (`icon=`, `theme=`, `highlight=`, `expandable`), e.g. ` ```go Go icon=code theme={"system"} `. Many markdown renderers — including those used by AI agents — treat the full string as the language hint, so syntax highlighting and code-block detection break. *(raised by @Fluf22 — unresolved)*

- `skills/algolia-migration/references/go.md:85` (and occurrences in python.md, csharp.md, java.md, javascript.md, php.md, ruby.md, scala.md, swift.md) — JSX/MDX components (`<Tip>`, `<Note>`, `</Tip>`, `</Note>`) appear as raw unrendered HTML in the markdown contexts AI agents use; the content inside them will not be visually distinguished and may confuse tool-call parsing. *(raised by @Fluf22 — unresolved)*

- `skills/algolia-migration/references/swift.md:19` (and occurrences in csharp.md, go.md, python.md, scala.md and others) — Absolute `/doc/` paths (e.g. `/doc/libraries/sdk/changelog/swift`, `/doc/libraries/sdk/methods/search/wait-for-task`) are broken outside the Algolia documentation site; agents following them hit 404s. *(raised by @Fluf22 — unresolved)*

### Suggestions

- `skills/algolia-migration/references/csharp.md` (and 8 other reference files — all except dart.md) — Missing trailing newline; can break `cat`, `diff`, and patch tooling. *(raised by @Fluf22 — unresolved)*

### Looks good

The kotlin.md removal and accompanying SKILL.md/evals/marketplace cleanup are clean. The validator passes 38/38 against the current local state.
