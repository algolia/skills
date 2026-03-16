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

errors: list[str] = []


def error(context: str, msg: str) -> None:
    errors.append(f"{context}: {msg}")


def validate_string_field(ctx: str, fm: dict, field: str, max_len: int, *, required: bool = True) -> str | None:
    value = fm.get(field)
    if value is None:
        if required:
            error(ctx, f"missing required field '{field}'")
        return None
    if not isinstance(value, str) or not value:
        error(ctx, f"'{field}' must be a non-empty string")
        return None
    if len(value) > max_len:
        error(ctx, f"'{field}' exceeds {max_len} chars ({len(value)})")
    return value


def validate_body_length(skill_dir: Path, body: str) -> None:
    stripped = body.strip()
    lines = stripped.splitlines() if stripped else []
    if len(lines) > BODY_MAX_LINES:
        error(
            skill_dir.name,
            f"SKILL.md body exceeds {BODY_MAX_LINES} lines ({len(lines)})",
        )


def validate_links(skill_dir: Path, body: str) -> None:
    for match in LINK_RE.finditer(body):
        rel_path = match.group(1).split("#")[0].strip()
        if not rel_path:
            continue
        target = skill_dir / rel_path
        if not target.exists():
            error(skill_dir.name, f"broken link: {rel_path}")


def validate_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        error(skill_dir.name, "missing SKILL.md")
        return

    content = skill_md.read_text(encoding="utf-8")

    # Parse frontmatter
    if not content.startswith("---"):
        error(skill_dir.name, "SKILL.md must start with YAML frontmatter (---)")
        return

    parts = content.split("---", 2)
    if len(parts) < 3:
        error(skill_dir.name, "SKILL.md has malformed frontmatter (missing closing ---)")
        return

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        error(skill_dir.name, f"invalid YAML frontmatter: {e}")
        return

    if not isinstance(fm, dict):
        error(skill_dir.name, "frontmatter must be a YAML mapping")
        return

    ctx = skill_dir.name
    name = validate_string_field(ctx, fm, "name", NAME_MAX_LEN)
    if name is not None:
        if not NAME_RE.match(name):
            error(ctx, f"'name' ({name!r}) invalid: must be lowercase alphanumeric + single hyphens, no leading/trailing hyphens")
        if name != skill_dir.name:
            error(ctx, f"'name' ({name!r}) must match directory name ({skill_dir.name!r})")

    validate_string_field(ctx, fm, "description", DESC_MAX_LEN)
    validate_string_field(ctx, fm, "compatibility", COMPAT_MAX_LEN, required=False)

    body = parts[2]
    validate_body_length(skill_dir, body)
    validate_links(skill_dir, body)


def validate_marketplace(root: Path) -> None:
    mp = root / ".claude-plugin" / "marketplace.json"
    if not mp.exists():
        return

    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error("marketplace.json", f"invalid JSON: {e}")
        return

    for plugin in data.get("plugins", []):
        for skill_path in plugin.get("skills", []):
            resolved = (root / skill_path).resolve()
            if not resolved.exists():
                error("marketplace.json", f"skill path does not exist: {skill_path}")
            elif not (resolved / "SKILL.md").exists():
                error("marketplace.json", f"skill path missing SKILL.md: {skill_path}")


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

    if errors:
        print(f"\n{len(errors)} error(s) found:\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print(f"✓ All {len(skill_dirs)} skill(s) passed validation")


if __name__ == "__main__":
    main()
