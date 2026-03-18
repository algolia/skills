#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Algolia CLI Skill — Integration Eval Runner
#
# Runs REAL Algolia CLI commands to validate that every command and flag
# documented in the skill actually works. Uses a source index as seed data
# and creates/cleans up temporary test indices.
#
# Prerequisites:
#   - `algolia` CLI installed (brew install algolia/algolia-cli/algolia)
#   - A configured profile with admin API key (`algolia profile list`)
#
# Usage:
#   ./run_cli_evals.sh                          # uses default source index
#   ./run_cli_evals.sh <source_index>           # uses custom source index
#   ALGOLIA_PROFILE=myprofile ./run_cli_evals.sh  # uses specific profile
# ──────────────────────────────────────────────────────────────────────────────
set -uo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
SOURCE_INDEX="${1:-algolia_movie_sample_dataset}"
TEST_PREFIX="cli_eval_$(date +%s)"
TEST_INDEX="${TEST_PREFIX}_products"
TEST_INDEX_V2="${TEST_PREFIX}_products_v2"
TEST_INDEX_SYN="${TEST_PREFIX}_synonyms"
TEST_INDEX_BACKUP="${TEST_PREFIX}_backup"
PROFILE_FLAG="${ALGOLIA_PROFILE:+-p $ALGOLIA_PROFILE}"
TMPDIR_EVAL=$(mktemp -d)

PASSED=0
FAILED=0
TOTAL=0

# ── Helpers ───────────────────────────────────────────────────────────────────
cleanup() {
  echo ""
  echo "═══ Cleanup ═══"
  for idx in "$TEST_INDEX" "$TEST_INDEX_V2" "$TEST_INDEX_SYN" "$TEST_INDEX_BACKUP"; do
    algolia indices delete "$idx" -y $PROFILE_FLAG 2>/dev/null && echo "  Deleted $idx" || echo "  Skip $idx (not found)"
  done
  # Delete any API key we created (stored in file)
  if [[ -f "$TMPDIR_EVAL/created_key" ]]; then
    local key
    key=$(cat "$TMPDIR_EVAL/created_key")
    algolia apikeys delete "$key" -y $PROFILE_FLAG 2>/dev/null && echo "  Deleted API key $key" || echo "  Skip API key deletion"
  fi
  rm -rf "$TMPDIR_EVAL"
  echo ""
}
trap cleanup EXIT

assert() {
  local description="$1"
  local exit_code="$2"
  TOTAL=$((TOTAL + 1))
  if [[ "$exit_code" -eq 0 ]]; then
    PASSED=$((PASSED + 1))
    echo "  ✅ $description"
  else
    FAILED=$((FAILED + 1))
    echo "  ❌ $description"
  fi
}

assert_file_not_empty() {
  local description="$1"
  local file="$2"
  TOTAL=$((TOTAL + 1))
  if [[ -s "$file" ]]; then
    PASSED=$((PASSED + 1))
    echo "  ✅ $description ($(wc -l < "$file" | tr -d ' ') lines)"
  else
    FAILED=$((FAILED + 1))
    echo "  ❌ $description (file empty or missing)"
  fi
}

assert_contains() {
  local description="$1"
  local file="$2"
  local pattern="$3"
  TOTAL=$((TOTAL + 1))
  if grep -q "$pattern" "$file" 2>/dev/null; then
    PASSED=$((PASSED + 1))
    echo "  ✅ $description"
  else
    FAILED=$((FAILED + 1))
    echo "  ❌ $description (pattern '$pattern' not found)"
  fi
}

assert_valid_json() {
  local description="$1"
  local file="$2"
  TOTAL=$((TOTAL + 1))
  if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$file" 2>/dev/null; then
    PASSED=$((PASSED + 1))
    echo "  ✅ $description"
  else
    FAILED=$((FAILED + 1))
    echo "  ❌ $description (invalid JSON)"
  fi
}

assert_valid_ndjson() {
  local description="$1"
  local file="$2"
  TOTAL=$((TOTAL + 1))
  local bad_lines
  bad_lines=$(while IFS= read -r line; do
    echo "$line" | python3 -c "import json,sys; json.loads(sys.stdin.read())" 2>/dev/null || echo "BAD"
  done < "$file" | grep -c "BAD" || true)
  if [[ "$bad_lines" -eq 0 ]] && [[ -s "$file" ]]; then
    PASSED=$((PASSED + 1))
    echo "  ✅ $description"
  else
    FAILED=$((FAILED + 1))
    echo "  ❌ $description ($bad_lines invalid lines)"
  fi
}

# ── Preflight ─────────────────────────────────────────────────────────────────
echo "═══ Algolia CLI Eval Runner ═══"
echo "Source index: $SOURCE_INDEX"
echo "Test prefix:  $TEST_PREFIX"
echo "Temp dir:     $TMPDIR_EVAL"
echo ""

echo "── Preflight: verify CLI and profile ──"
algolia profile list $PROFILE_FLAG > /dev/null 2>&1
assert "CLI is installed and profile is configured" $?

# Verify source index exists
algolia search "$SOURCE_INDEX" --query "" --hitsPerPage 1 $PROFILE_FLAG > /dev/null 2>&1
assert "Source index '$SOURCE_INDEX' is accessible" $?

echo ""

# ══════════════════════════════════════════════════════════════════════════════
# EVAL 1: Migrate records between indices
# Covers: objects browse, objects import (no -y!), settings set, -w flag, pipes
# ══════════════════════════════════════════════════════════════════════════════
echo "═══ Eval 1: Migrate Records Between Indices ═══"

# 1a. Browse with --attributesToRetrieve and export to file
echo "── 1a: objects browse with --attributesToRetrieve ──"
algolia objects browse "$SOURCE_INDEX" \
  --attributesToRetrieve objectID,title,year \
  $PROFILE_FLAG > "$TMPDIR_EVAL/browse_filtered.ndjson" 2>/dev/null
assert "objects browse with --attributesToRetrieve succeeds" $?
assert_file_not_empty "Browse output contains records" "$TMPDIR_EVAL/browse_filtered.ndjson"
assert_valid_ndjson "Browse output is valid ndjson" "$TMPDIR_EVAL/browse_filtered.ndjson"

# 1b. Import from file (NO -y flag — it doesn't exist on this command)
echo "── 1b: objects import from file (no -y) ──"
head -20 "$TMPDIR_EVAL/browse_filtered.ndjson" > "$TMPDIR_EVAL/import_sample.ndjson"
algolia objects import "$TEST_INDEX" \
  -F "$TMPDIR_EVAL/import_sample.ndjson" \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "objects import from file succeeds (without -y)" $?

# 1c. Pipe browse → import (the documented pattern)
echo "── 1c: pipe browse → import via stdin ──"
# Use a pre-sliced file to avoid SIGPIPE from head cutting off browse mid-stream
head -10 "$TMPDIR_EVAL/browse_filtered.ndjson" > "$TMPDIR_EVAL/pipe_sample.ndjson"
cat "$TMPDIR_EVAL/pipe_sample.ndjson" \
  | algolia objects import "$TEST_INDEX_V2" \
      -F - \
      -w \
      $PROFILE_FLAG > /dev/null 2>&1
assert "Pipe stdin → import with -F - succeeds" $?

# 1d. settings set with --attributesForFaceting
echo "── 1d: settings set ──"
algolia settings set "$TEST_INDEX" \
  --attributesForFaceting "year" \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "settings set --attributesForFaceting succeeds (without -y)" $?

# 1e. Verify settings were applied
echo "── 1e: settings get to verify ──"
algolia settings get "$TEST_INDEX" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/settings_verify.json" 2>/dev/null
assert "settings get succeeds" $?
assert_contains "attributesForFaceting includes 'year'" "$TMPDIR_EVAL/settings_verify.json" "year"

# 1f. Verify -y flag does NOT exist on objects import
echo "── 1f: verify -y is rejected by objects import ──"
if algolia objects import "$TEST_INDEX" -F "$TMPDIR_EVAL/import_sample.ndjson" -y $PROFILE_FLAG > /dev/null 2>&1; then
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1))
  echo "  ❌ objects import should reject -y flag but didn't"
else
  TOTAL=$((TOTAL + 1)); PASSED=$((PASSED + 1))
  echo "  ✅ objects import correctly rejects -y flag"
fi

echo ""

# ══════════════════════════════════════════════════════════════════════════════
# EVAL 2: Synonyms and Rules
# Covers: synonyms save, synonyms import, synonyms browse, rules import -y,
#         ndjson format, synonym types
# ══════════════════════════════════════════════════════════════════════════════
echo "═══ Eval 2: Synonyms and Rules ═══"

# Seed the synonym test index with a few records
echo "── 2a: seed test index for synonyms ──"
head -20 "$TMPDIR_EVAL/browse_filtered.ndjson" \
  | algolia objects import "$TEST_INDEX_SYN" -F - -w $PROFILE_FLAG > /dev/null 2>&1
assert "Seed synonym test index" $?

# 2b. synonyms save — regular (two-way)
echo "── 2b: synonyms save (regular two-way) ──"
algolia synonyms save "$TEST_INDEX_SYN" \
  --id "syn-eval-regular" \
  --synonyms sneakers,trainers \
  --wait \
  $PROFILE_FLAG > /dev/null 2>&1
assert "synonyms save (regular) succeeds" $?

# 2c. synonyms save — one-way
echo "── 2c: synonyms save (one-way) ──"
algolia synonyms save "$TEST_INDEX_SYN" \
  --id "syn-eval-oneway" \
  --type oneWaySynonym \
  --input "TV" \
  --synonyms "television,flat screen" \
  --wait \
  $PROFILE_FLAG > /dev/null 2>&1
assert "synonyms save (oneway) succeeds" $?

# 2d. synonyms browse — verify they exist
echo "── 2d: synonyms browse ──"
algolia synonyms browse "$TEST_INDEX_SYN" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/synonyms_browse.ndjson" 2>/dev/null
assert "synonyms browse succeeds" $?
assert_contains "Regular synonym exists" "$TMPDIR_EVAL/synonyms_browse.ndjson" "syn-eval-regular"
assert_contains "One-way synonym exists" "$TMPDIR_EVAL/synonyms_browse.ndjson" "syn-eval-oneway"

# 2e. synonyms import from ndjson file (no -y flag)
echo "── 2e: synonyms import from ndjson ──"
cat > "$TMPDIR_EVAL/synonyms_import.ndjson" <<'NDJSON'
{"objectID":"syn-eval-imported","type":"synonym","synonyms":["film","movie","picture"]}
NDJSON
algolia synonyms import "$TEST_INDEX_SYN" \
  -F "$TMPDIR_EVAL/synonyms_import.ndjson" \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "synonyms import from ndjson succeeds (without -y)" $?

# 2f. rules import with -y (rules import DOES have -y)
echo "── 2f: rules import with -y ──"
cat > "$TMPDIR_EVAL/rules_import.ndjson" <<'NDJSON'
{"objectID":"rule-eval-boost","description":"Boost featured items","conditions":[{"anchoring":"is","pattern":"","alternatives":false,"context":"featured"}],"consequence":{"params":{"optionalFilters":["featured:true"]}}}
NDJSON
algolia rules import "$TEST_INDEX_SYN" \
  -F "$TMPDIR_EVAL/rules_import.ndjson" \
  -y \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "rules import with -y succeeds" $?

# 2g. rules browse — verify rule exists
echo "── 2g: rules browse ──"
algolia rules browse "$TEST_INDEX_SYN" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/rules_browse.ndjson" 2>/dev/null
assert "rules browse succeeds" $?
assert_contains "Imported rule exists" "$TMPDIR_EVAL/rules_browse.ndjson" "rule-eval-boost"

# 2h. synonyms delete with -y
echo "── 2h: synonyms delete with -y ──"
algolia synonyms delete "$TEST_INDEX_SYN" \
  --synonym-ids "syn-eval-imported" \
  -y \
  --wait \
  $PROFILE_FLAG > /dev/null 2>&1
assert "synonyms delete with -y succeeds" $?

# 2i. rules delete with -y
echo "── 2i: rules delete with -y ──"
algolia rules delete "$TEST_INDEX_SYN" \
  --rule-ids "rule-eval-boost" \
  -y \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "rules delete with -y succeeds" $?

echo ""

# ══════════════════════════════════════════════════════════════════════════════
# EVAL 3: Full Backup, Restore, and API Key
# Covers: objects browse → ndjson, settings get → json, rules browse → ndjson,
#         synonyms browse → ndjson, apikeys create, apikeys delete,
#         objects import (restore), settings import, rules import -c -y,
#         synonyms import -r
# ══════════════════════════════════════════════════════════════════════════════
echo "═══ Eval 3: Full Backup and Restore ═══"

# 3a. Full backup — records
echo "── 3a: backup records (objects browse) ──"
algolia objects browse "$TEST_INDEX_SYN" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/backup_records.ndjson" 2>/dev/null
assert "objects browse for backup succeeds" $?
assert_valid_ndjson "Backup records are valid ndjson" "$TMPDIR_EVAL/backup_records.ndjson"

# 3b. Full backup — settings
echo "── 3b: backup settings (settings get) ──"
algolia settings get "$TEST_INDEX_SYN" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/backup_settings.json" 2>/dev/null
assert "settings get for backup succeeds" $?
assert_valid_json "Backup settings are valid JSON (not ndjson)" "$TMPDIR_EVAL/backup_settings.json"

# 3c. Full backup — rules
echo "── 3c: backup rules (rules browse) ──"
algolia rules browse "$TEST_INDEX_SYN" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/backup_rules.ndjson" 2>/dev/null
assert "rules browse for backup succeeds" $?

# 3d. Full backup — synonyms
echo "── 3d: backup synonyms (synonyms browse) ──"
algolia synonyms browse "$TEST_INDEX_SYN" \
  $PROFILE_FLAG > "$TMPDIR_EVAL/backup_synonyms.ndjson" 2>/dev/null
assert "synonyms browse for backup succeeds" $?
assert_valid_ndjson "Backup synonyms are valid ndjson" "$TMPDIR_EVAL/backup_synonyms.ndjson"

# 3e. Restore — import records into a fresh index
echo "── 3e: restore records (objects import) ──"
algolia objects import "$TEST_INDEX_BACKUP" \
  -F "$TMPDIR_EVAL/backup_records.ndjson" \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "objects import for restore succeeds" $?

# 3f. Restore — import settings
echo "── 3f: restore settings (settings import) ──"
algolia settings import "$TEST_INDEX_BACKUP" \
  -F "$TMPDIR_EVAL/backup_settings.json" \
  -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "settings import for restore succeeds (without -y)" $?

# 3g. Restore — import rules with -c (clear existing) and -y
echo "── 3g: restore rules (rules import -c -y) ──"
# Create a valid minimal rules file if backup was empty
if [[ ! -s "$TMPDIR_EVAL/backup_rules.ndjson" ]]; then
  echo '{"objectID":"eval-placeholder-rule","description":"placeholder","conditions":[{"anchoring":"contains","pattern":"eval-test"}],"consequence":{"params":{"query":"eval-test"}}}' > "$TMPDIR_EVAL/backup_rules.ndjson"
fi
algolia rules import "$TEST_INDEX_BACKUP" \
  -F "$TMPDIR_EVAL/backup_rules.ndjson" \
  -c -y -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "rules import -c -y for restore succeeds" $?

# 3h. Restore — import synonyms with -r (replace existing)
echo "── 3h: restore synonyms (synonyms import -r) ──"
algolia synonyms import "$TEST_INDEX_BACKUP" \
  -F "$TMPDIR_EVAL/backup_synonyms.ndjson" \
  -r -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "synonyms import -r for restore succeeds (without -y)" $?

# 3i. API key create
echo "── 3i: apikeys create ──"
# Capture keys before creation
algolia apikeys list $PROFILE_FLAG 2>/dev/null | awk '{print $1}' | sort > "$TMPDIR_EVAL/keys_before.txt"
algolia apikeys create \
  --acl search \
  --indices "$TEST_INDEX_BACKUP" \
  --description "eval-test-key-$TEST_PREFIX" \
  $PROFILE_FLAG > /dev/null 2>&1
assert "apikeys create succeeds" $?

# Extract the new key by diffing before/after
sleep 2
algolia apikeys list $PROFILE_FLAG 2>/dev/null | awk '{print $1}' | sort > "$TMPDIR_EVAL/keys_after.txt"
CREATED_KEY=$(comm -13 "$TMPDIR_EVAL/keys_before.txt" "$TMPDIR_EVAL/keys_after.txt" | head -1 || true)
if [[ -z "$CREATED_KEY" ]]; then
  # Fallback: find by description
  CREATED_KEY=$(algolia apikeys list $PROFILE_FLAG 2>/dev/null | grep "eval-test-key-$TEST_PREFIX" | awk '{print $1}' | head -1 || true)
fi
if [[ -n "$CREATED_KEY" ]]; then
  echo "$CREATED_KEY" > "$TMPDIR_EVAL/created_key"
  echo "  (created key: ${CREATED_KEY:0:8}...)"
fi

# 3j. API key get
echo "── 3j: apikeys get ──"
if [[ -n "$CREATED_KEY" ]]; then
  algolia apikeys get "$CREATED_KEY" $PROFILE_FLAG > /dev/null 2>&1
  assert "apikeys get succeeds" $?
else
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1))
  echo "  ❌ apikeys get — could not identify created key"
fi

echo ""

# ══════════════════════════════════════════════════════════════════════════════
# EVAL 4: Index Management
# Covers: indices copy, indices clear, search, objects delete, objects update
# ══════════════════════════════════════════════════════════════════════════════
echo "═══ Eval 4: Index Management ═══"

# 4a. indices copy (with -y)
echo "── 4a: indices copy ──"
algolia indices copy "$TEST_INDEX" "$TEST_INDEX_V2" \
  -y -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "indices copy with -y succeeds" $?

# 4b. search
echo "── 4b: search ──"
algolia search "$TEST_INDEX_V2" \
  --query "" \
  --hitsPerPage 5 \
  $PROFILE_FLAG > "$TMPDIR_EVAL/search_results.json" 2>/dev/null
assert "search succeeds" $?
assert_valid_json "Search output is valid JSON" "$TMPDIR_EVAL/search_results.json"

# 4c. objects update (no -y)
echo "── 4c: objects update ──"
# Get a real objectID from the index
FIRST_ID=$(head -1 "$TMPDIR_EVAL/browse_filtered.ndjson" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['objectID'])" 2>/dev/null || echo "")
if [[ -n "$FIRST_ID" ]]; then
  echo "{\"objectID\":\"$FIRST_ID\",\"eval_tag\":\"updated\"}" > "$TMPDIR_EVAL/update.ndjson"
  algolia objects update "$TEST_INDEX" \
    -F "$TMPDIR_EVAL/update.ndjson" \
    -w \
    $PROFILE_FLAG > /dev/null 2>&1
  assert "objects update succeeds (without -y)" $?
else
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1))
  echo "  ❌ objects update — couldn't extract objectID"
fi

# 4d. objects delete with -y
echo "── 4d: objects delete ──"
if [[ -n "$FIRST_ID" ]]; then
  algolia objects delete "$TEST_INDEX" \
    --object-ids "$FIRST_ID" \
    -y --wait \
    $PROFILE_FLAG > /dev/null 2>&1
  assert "objects delete --object-ids with -y succeeds" $?
else
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1))
  echo "  ❌ objects delete — no objectID available"
fi

# 4e. indices clear with -y
echo "── 4e: indices clear ──"
algolia indices clear "$TEST_INDEX_V2" \
  -y -w \
  $PROFILE_FLAG > /dev/null 2>&1
assert "indices clear with -y succeeds" $?

echo ""

# ══════════════════════════════════════════════════════════════════════════════
# EVAL 5: Negative Tests — verify invalid flags are rejected
# ══════════════════════════════════════════════════════════════════════════════
echo "═══ Eval 5: Negative Tests (invalid flags must fail) ═══"

# 5a. objects import -y must fail
echo "── 5a: objects import -y (must fail) ──"
if algolia objects import "$TEST_INDEX" -F "$TMPDIR_EVAL/import_sample.ndjson" -y $PROFILE_FLAG > /dev/null 2>&1; then
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1)); echo "  ❌ objects import -y should be rejected"
else
  TOTAL=$((TOTAL + 1)); PASSED=$((PASSED + 1)); echo "  ✅ objects import -y correctly rejected"
fi

# 5b. objects update -y must fail
echo "── 5b: objects update -y (must fail) ──"
if algolia objects update "$TEST_INDEX" -F "$TMPDIR_EVAL/update.ndjson" -y $PROFILE_FLAG > /dev/null 2>&1; then
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1)); echo "  ❌ objects update -y should be rejected"
else
  TOTAL=$((TOTAL + 1)); PASSED=$((PASSED + 1)); echo "  ✅ objects update -y correctly rejected"
fi

# 5c. settings set -y must fail
echo "── 5c: settings set -y (must fail) ──"
if algolia settings set "$TEST_INDEX" --typoTolerance="false" -y $PROFILE_FLAG > /dev/null 2>&1; then
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1)); echo "  ❌ settings set -y should be rejected"
else
  TOTAL=$((TOTAL + 1)); PASSED=$((PASSED + 1)); echo "  ✅ settings set -y correctly rejected"
fi

# 5d. settings import -y must fail
echo "── 5d: settings import -y (must fail) ──"
if algolia settings import "$TEST_INDEX" -F "$TMPDIR_EVAL/backup_settings.json" -y $PROFILE_FLAG > /dev/null 2>&1; then
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1)); echo "  ❌ settings import -y should be rejected"
else
  TOTAL=$((TOTAL + 1)); PASSED=$((PASSED + 1)); echo "  ✅ settings import -y correctly rejected"
fi

# 5e. synonyms import -y must fail
echo "── 5e: synonyms import -y (must fail) ──"
if algolia synonyms import "$TEST_INDEX_SYN" -F "$TMPDIR_EVAL/synonyms_import.ndjson" -y $PROFILE_FLAG > /dev/null 2>&1; then
  TOTAL=$((TOTAL + 1)); FAILED=$((FAILED + 1)); echo "  ❌ synonyms import -y should be rejected"
else
  TOTAL=$((TOTAL + 1)); PASSED=$((PASSED + 1)); echo "  ✅ synonyms import -y correctly rejected"
fi

echo ""

# ══════════════════════════════════════════════════════════════════════════════
# Results
# ══════════════════════════════════════════════════════════════════════════════
echo "══════════════════════════════════════════"
echo "  Results: $PASSED/$TOTAL passed, $FAILED failed"
echo "══════════════════════════════════════════"

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
