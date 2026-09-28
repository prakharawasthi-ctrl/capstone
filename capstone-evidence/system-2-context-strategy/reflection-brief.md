# Reflection brief — System 2 context strategy (run 20260928-234316)

All numbers below are my own, from `budget.json` produced by
`solution/offline_build.py` (methodology: `len(text) / 3.8 heuristic (no API key
available)`). Baseline `47144` tokens; assembled `20236` tokens; reduction
`57.08%`. Per-section tokens: `case_facts 149`, `resolved_refund 272`,
`resolved_subscription 276`, `active 19538`.

## What was summarized

Resolved threads only — refund (turns 1–14, `13921` input tokens → `264`-token
summary) and subscription (turns 15–28, `13693` → `265`) — each condensed into
the committed prompt shape (`**Outcome.** / **Key facts.** / **Resolution.**`,
`prompts/compression_prompt.md`, ≤500 tokens). These narratives are safe to
compress because their facts stabilized: the refund closed as processed, the
subscription closed as cancelled with a prorated refund. The summaries preserve
every decision-relevant value verbatim (`ORD-77310`, `$22.14`, `SUB-22119`,
`duplicate_charge`, `cancelled_with_prorated_refund`, `Pantry Plus Monthly`) and
shed only turn-by-turn prose, which is why the resolved portion compresses
~97% (27614 → 548 tokens) and sits in the low-attention middle of the assembly
(the lost-in-the-middle-tolerant zone). The pruner applies the same logic at
field granularity: `prune_lookup_order` keeps exactly 5 of 57 tool fields
(`order_id, order_date, order_total_usd, fulfillment_status,
return_eligible_until`), measured `532 → 45` tokens.

## What was preserved verbatim, and why

Two blocks are never summarized. (1) The 12-field `CaseFacts` block (`149`
tokens) at the top boundary — dense structured state (`customer_id`,
`refund_amount_usd`, `payment_update_status`, etc.) the model needs without
scanning narrative. (2) The active payment-update segment, turns 29–48
(`19538` tokens, ~96.5% of the assembly), byte-exact (`active_raw_text ==`
joined turn renders; enforced by `test_active_segment_byte_exact` and the
run-artifact audit). It dominates the budget because the issue is still open:
failure code `AVS_MISMATCH`, new-card last-4 `7782`, and the evolving retry
state are potentially decision-load-bearing on the next turn, so any
summarization would risk fidelity loss where it matters most. Placing case
facts at the top and the active verbatim at the bottom puts the densest and
freshest content at the two high-attention boundaries, deliberately deviating
from the pass-complete-history baseline only for resolved threads where
coherence is no longer load-bearing. `compressor.summarize_segment` refuses the
active segment (`ValueError`) so this rule holds in code, not just convention.

## Control proof the facts block is load-bearing

Full-context eval (`eval.jsonl`): 6/6 pass — Q1 `$22.14`, Q2 `duplicate`, Q3
`AVS_MISMATCH`, Q4 `7782`, Q5 `prorated`, Q6 `in_progress`. Case-facts-stripped
control (`eval_control.jsonl`, via `evaluate.strip_case_facts`, Q1+Q6 only): Q1
still passes (the refund summary redundantly preserves `$22.14`, so case facts
is the cheaper path, not the only path) while Q6 regresses to FAIL
(`answer=unknown`). The snake_case token `in_progress` appears nowhere in the
48-turn transcript prose or the resolved summaries — it lives only in the
case-facts block — so stripping the block removes the only source. That single
regression is the empirical proof the persistent block carries information the
summaries plus active verbatim do not.
