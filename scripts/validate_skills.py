#!/usr/bin/env python3
"""Validate Agent Skills against the agentskills.io specification.

Checks:
  - SKILL.md exists in each skill directory
  - Valid YAML frontmatter
  - Required fields: name, description
  - name: 1-64 chars, lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphens, matches directory name
  - description: 1-1024 chars
  - compatibility (if present): 1-500 chars
  - Body: under 500 lines
  - Relative markdown links resolve to existing files
  - marketplace.json: valid JSON, referenced skill paths exist

Reference: https://agentskills.io/specification
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml")
    sys.exit(1)

# --- Spec limits ---
NAME_MAX_LEN = 64
DESC_MAX_LEN = 1024
COMPAT_MAX_LEN = 500
BODY_MAX_LINES = 500
NAME_RE = re.compile(r"^[a-z0-9](-?[a-z0-9])*$")
LINK_RE = re.compile(r"\[.*?]\(((?!https?://|#|mailto:).*?)\)")


class Report:
    def __init__(self) -> None:
        self._results: list[tuple[str, bool, str]] = []

    def pass_(self, ctx: str, msg: str) -> None:
        self._results.append((ctx, True, msg))

    def fail_(self, ctx: str, msg: str) -> None:
        self._results.append((ctx, False, msg))

    @property
    def has_failures(self) -> bool:
        return any(not ok for _, ok, _ in self._results)

    def print_summary(self) -> None:
        # Group by context, preserving insertion order
        contexts: dict[str, list[tuple[bool, str]]] = {}
        for ctx, ok, msg in self._results:
            contexts.setdefault(ctx, []).append((ok, msg))

        passed = sum(1 for _, ok, _ in self._results if ok)
        failed = sum(1 for _, ok, _ in self._results if not ok)

        for ctx, checks in contexts.items():
            print(ctx)
            for ok, msg in checks:
                mark = "✓" if ok else "✗"
                print(f"  {mark} {msg}")
            print()

        print(f"Results: {passed} passed, {failed} failed")


report = Report()


def validate_string_field(ctx: str, fm: dict, field: str, max_len: int, *, required: bool = True) -> str | None:
    value = fm.get(field)
    if value is None:
        if required:
            report.fail_(ctx, f"required field '{field}': missing")
        return None
    if not isinstance(value, str) or not value:
        report.fail_(ctx, f"'{field}' must be a non-empty string")
        return None
    if len(value) > max_len:
        report.fail_(ctx, f"'{field}' exceeds {max_len} chars ({len(value)})")
        return value
    return value


def validate_body_length(skill_dir: Path, body: str) -> None:
    ctx = skill_dir.name
    stripped = body.strip()
    lines = stripped.splitlines() if stripped else []
    if len(lines) > BODY_MAX_LINES:
        report.fail_(ctx, f"body length: exceeds {BODY_MAX_LINES} lines ({len(lines)})")
    else:
        report.pass_(ctx, f"body length ({len(lines)} lines)")


def validate_links(skill_dir: Path, body: str) -> None:
    ctx = skill_dir.name
    broken = []
    for match in LINK_RE.finditer(body):
        rel_path = match.group(1).split("#")[0].strip()
        if not rel_path:
            continue
        target = skill_dir / rel_path
        if not target.exists():
            broken.append(rel_path)

    if broken:
        for link in broken:
            report.fail_(ctx, f"relative links: broken link {link}")
    else:
        report.pass_(ctx, "relative links")


def validate_skill(skill_dir: Path) -> None:
    ctx = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.fail_(ctx, "SKILL.md exists: missing")
        return

    report.pass_(ctx, "SKILL.md exists")

    content = skill_md.read_text(encoding="utf-8")

    # Parse frontmatter
    if not content.startswith("---"):
        report.fail_(ctx, "valid YAML frontmatter: must start with ---")
        return

    parts = content.split("---", 2)
    if len(parts) < 3:
        report.fail_(ctx, "valid YAML frontmatter: missing closing ---")
        return

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        report.fail_(ctx, f"valid YAML frontmatter: {e}")
        return

    if not isinstance(fm, dict):
        report.fail_(ctx, "valid YAML frontmatter: must be a YAML mapping")
        return

    report.pass_(ctx, "valid YAML frontmatter")

    # Required fields
    name = validate_string_field(ctx, fm, "name", NAME_MAX_LEN)
    desc = validate_string_field(ctx, fm, "description", DESC_MAX_LEN)
    if name is not None and desc is not None:
        report.pass_(ctx, "required fields (name, description)")
    elif name is None and desc is None:
        pass  # individual failures already recorded
    else:
        pass  # individual failure already recorded

    # Name format & directory match
    if name is not None:
        name_ok = True
        if not NAME_RE.match(name):
            report.fail_(ctx, f"name format: {name!r} invalid — must be lowercase alphanumeric + single hyphens")
            name_ok = False
        if name != skill_dir.name:
            report.fail_(ctx, f"name format: {name!r} must match directory name {skill_dir.name!r}")
            name_ok = False
        if name_ok:
            report.pass_(ctx, "name format and directory match")

    validate_string_field(ctx, fm, "compatibility", COMPAT_MAX_LEN, required=False)

    body = parts[2]
    validate_body_length(skill_dir, body)
    validate_links(skill_dir, body)


def validate_marketplace(root: Path) -> None:
    ctx = "marketplace.json"
    mp = root / ".claude-plugin" / "marketplace.json"
    if not mp.exists():
        return

    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        report.fail_(ctx, f"valid JSON: {e}")
        return

    report.pass_(ctx, "valid JSON")

    all_exist = True
    for plugin in data.get("plugins", []):
        for skill_path in plugin.get("skills", []):
            resolved = (root / skill_path).resolve()
            if not resolved.exists():
                report.fail_(ctx, f"skill paths exist: {skill_path} not found")
                all_exist = False
            elif not (resolved / "SKILL.md").exists():
                report.fail_(ctx, f"skill paths exist: {skill_path} missing SKILL.md")
                all_exist = False

    if all_exist:
        report.pass_(ctx, "skill paths exist")

    # Inverse check: every skill on disk must be registered in marketplace.json
    skills_dir = root / "skills"
    if skills_dir.exists():
        registered = set()
        for plugin in data.get("plugins", []):
            for skill_path in plugin.get("skills", []):
                resolved = (root / skill_path).resolve()
                registered.add(resolved)

        all_registered = True
        for skill_dir in sorted(d for d in skills_dir.iterdir() if d.is_dir()):
            if skill_dir.resolve() not in registered:
                report.fail_(ctx, f"unregistered skill: {skill_dir.name} exists in skills/ but is not listed in marketplace.json")
                all_registered = False

        if all_registered:
            report.pass_(ctx, "all skills registered in marketplace.json")


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    skills_dir = root / "skills"

    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        sys.exit(1)

    skill_dirs = sorted(d for d in skills_dir.iterdir() if d.is_dir())
    if not skill_dirs:
        print("No skill directories found")
        sys.exit(1)

    for skill_dir in skill_dirs:
        validate_skill(skill_dir)

    validate_marketplace(root)

    report.print_summary()
    if report.has_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
