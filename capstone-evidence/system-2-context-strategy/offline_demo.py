"""Offline deterministic context measurements for System 2 (no API key required).

Uses ONLY deterministic, non-LLM code paths:
- transcript.load + token_count (baseline)
- pruner.prune_lookup_order (verbose tool output pruning)
- assemble.build with synthetic resolved summaries + REAL active verbatim

Resolved summaries here are SYNTHETIC placeholders (not LLM output) and are
clearly labeled as such. No eval questions are executed. This demonstrates the
assembly/token-accounting mechanism, not the 6-question eval results.
"""
import json
import sys
from pathlib import Path

SOL = Path(__file__).resolve().parents[2] / "Engineer a Long-Conversation Context Strategy for a Retail Support Copilot/04-assemble-and-locate/solution"
sys.path.insert(0, str(SOL))

from retail_context import transcript
from retail_context.assemble import build
from retail_context.case_facts import CaseFacts
from retail_context.compressor import Compressed, Summary
from retail_context.pruner import KEPT_FIELDS, prune_lookup_order
from retail_context.tokens import count, methodology

DATA = SOL / "data"

t = transcript.load(DATA / "transcript_48turns.json")
print(f"methodology: {methodology()}")
print(f"baseline transcript tokens: {t.token_count}")
print(f"turns: {len(t.turns)} refund={t.segment('refund').turn_range} subscription={t.segment('subscription').turn_range} active={t.segment('payment_update').turn_range}")

raw = json.loads((DATA / "lookup_order_response.json").read_text())
print(f"lookup_order raw fields: {len(raw)}")
pruned = prune_lookup_order(raw)
print(f"pruned fields: {tuple(pruned.keys())} (contract: {KEPT_FIELDS})")
print(f"raw tokens: {count(json.dumps(raw))} pruned tokens: {count(json.dumps(pruned))}")

facts = CaseFacts(
    customer_id="CUST-88421", refund_order_id="ORD-77310", refund_amount_usd=22.14,
    refund_status="processed", subscription_id="SUB-22119",
    subscription_plan="Pantry Plus Monthly", subscription_cancel_reason="duplicate_charge",
    subscription_status="cancelled_with_prorated_refund",
    active_payment_method_last4="4242", new_payment_method_last4="7782",
    payment_update_failure_code="AVS_MISMATCH", payment_update_status="in_progress",
)
active_text = "\n\n".join(turn.render() for turn in t.active_turns)
compressed = Compressed(
    summaries={
        "refund": Summary(issue_id="refund", text="[SYNTHETIC placeholder — not LLM output] Refund for ORD-77310 processed for $22.14.", input_tokens=0, output_tokens=0),
        "subscription": Summary(issue_id="subscription", text="[SYNTHETIC placeholder — not LLM output] Subscription SUB-22119 cancelled (duplicate_charge) with prorated refund.", input_tokens=0, output_tokens=0),
    },
    active_text=active_text, active_issue_id="payment_update",
)
assembled = build(facts, compressed)
sec = assembled.section_tokens()
total = assembled.total_tokens()
print("per-section tokens (SYNTHETIC resolved summaries):")
for k, v in sec.items():
    print(f"  {k}: {v}")
print(f"assembled total: {total}")
print(f"reduction vs baseline: {round((1 - total / t.token_count) * 100, 2)}% (with synthetic summaries — NOT the reference 56.83% eval number)")
print(f"active byte-exact check: {assembled.active_raw_text == active_text}")
print(f"case facts header present: {'# Case Facts' in assembled.markdown}")
