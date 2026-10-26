# Eval report: <AGENT_NAME>, <DATE>

Fill every section. Leave a section in place with "not measured" rather than
deleting it, and move anything you did not verify to "Unverified".

## Run card

Paste the run card of the baseline and of each candidate
([run-card.md](run-card.md)). Flag any line marked "must match" that differs.

## Results on shared cases

Computed on the cases both runs share (`compare` reports `sharedCases`; or
`python3 "$SKILL_DIR/scripts/compare_runs.py" DIR_A DIR_B`). Deltas are B - A.

| Metric | Shared cases | A pass rate | B pass rate | Delta | Delta 95% CI | Verdict |
|---|---|---|---|---|---|---|
| tone | | | | | | improved / regressed / within noise / directional only |
| faithfulness | | | | | | |
| relevance | | | | | | |

Verdicts follow [Statistics rules](../references/evaluations.md#statistics-rules)
(headroom, sample size, CI).

## Efficiency

| Run | Mean input tokens | Median input tokens | Mean output tokens | Mean duration | Median duration |
|---|---|---|---|---|---|
| A (baseline) | | | | | |
| B (candidate) | | | | | |
| Change | | | | | |

## Failure themes and instrument check

| Theme | Metric | Count | Example reason (paraphrased) | Knob |
|---|---|---|---|---|
| | | | | |

Instrument check: passed | failed | not run. Cases checked: <caseId>, <caseId>.
`responseText` score vs `answerText` score: <...>. If failed, which themes are
instrument artifacts and were excluded from tuning.

## What changed

- Instructions diff (summary, full diff attached):
- Tools diff (for example Search tool `searchParameters`):
- Config diff:
- Rollback snapshot path: `<SNAPSHOT_DIR>/agent-config.json`

## Decision options

| Option | Expected effect | Cost to verify further | Risk |
|---|---|---|---|
| Promote now | | none | |
| Run a larger confirmation (n per metric = ) | | <cases> completions + judge calls | |
| Iterate on <theme> | | | |
| Stop, keep production unchanged | | none | |

Gate status against the [Promotion gate](../references/evaluations.md#promotion-gate):
met | not met (<which condition fails>).

## Unverified

- <claims you believe but did not measure, for example "faithfulness is not
  skewed by display-tool values">
