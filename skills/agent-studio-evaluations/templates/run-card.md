# Run card

Print this card before every paid run (baseline, candidate, smoke test,
confirmation). Two runs are comparable only when their cards match on every
line marked "must match". Refuse to compare runs whose dataset ids differ.

```text
RUN CARD
Purpose:            baseline | candidate | smoke test | confirmation
Agent:              <AGENT_ID>  (<name>, status: draft | published)
Index:              <INDEX_NAME>
Dataset id:         <DATASET_ID>          must match
Dataset name:       <DATASET_NAME>
Dataset source:     generated | imported (real history) | merged
agentProfileId:     <AGENT_PROFILE_ID>    built on the SOURCE agent
indexProfileId:     <INDEX_PROFILE_ID>    must match
Metrics:            <slug>=<metricId>, ...  must match
Cases per metric:   tone=<n>, faithfulness=<n>, relevance=<n>, ...
--num-cases:        <total> (a TOTAL split across metrics)
Iterations:         1
Tone contracts:     <k> distinct
  1. tone_constraint: "<...>"
     specific_rule:   "<...>"
     matches agent voice: yes | no (rewrite before running)
Estimated cost:     <cases> completions + <cases> judge calls
Instrument check:   pending | passed | failed (see evaluations.md)
```

Where the values come from:

- Dataset id and profile ids: `algobot evals datasets get <DATASET_ID>`, or
  the resolved refs in `algobot evals experiments get <EXPERIMENT_ID>`.
- Cases per metric: `algobot evals datasets list-cases <DATASET_ID> --metric-slug <slug> --limit 200`
  (page with `--offset`), or count after `python3 "$SKILL_DIR/scripts/fetch_run.py"` (`SKILL_DIR` is
  the directory containing this skill's `SKILL.md`).
- Tone contracts: the distinct `expected.tone_constraint` and
  `expected.specific_rule` values of the tone cases.
- Agent voice: the OUTPUT STYLE (or equivalent) section of
  `algobot agents get <AGENT_ID>` instructions.

Always pass `--dataset-id <DATASET_ID>` on `experiments create` for any run
you intend to compare.
