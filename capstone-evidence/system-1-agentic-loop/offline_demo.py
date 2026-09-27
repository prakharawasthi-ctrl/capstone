"""Offline stop_reason demonstration for System 1 (no API key required).

Uses the REAL claims_intake.loop.run + REAL tool executor + REAL ClaimSession,
with a scripted FakeClient standing in for the Anthropic API. This exercises
the identical continue-on-tool_use / stop-on-end_turn contract without spend.
"""
import json
import sys
import tempfile
from pathlib import Path

SOL = Path(__file__).resolve().parents[2] / "Build a Claims Intake Agent with a stop_reason-Driven Loop/exercises/03-dynamic-decomposition/solution"
sys.path.insert(0, str(SOL))

from claims_intake.budget import Budget
from claims_intake.loop import run as run_loop
from claims_intake.session import ClaimSession
from claims_intake.tools import TOOL_SCHEMAS, make_executor
from claims_intake.tracer import Tracer
from tests.fakes import FakeBlock, FakeClient, FakeMessages, FakeResponse, FakeUsage

ROOT = Path(__file__).resolve().parents[2] / "Build a Claims Intake Agent with a stop_reason-Driven Loop/exercises/03-dynamic-decomposition/solution"
policies = json.loads((ROOT / "data" / "policies.json").read_text())
fixture = json.loads((ROOT / "fixtures" / "claims" / "claim_01_kitchen_fire.json").read_text())

tmp = Path(tempfile.mkdtemp(prefix="claims_offline_"))
run_dir = tmp / "run"
run_dir.mkdir(parents=True, exist_ok=True)

session = ClaimSession(
    claim_id=fixture["claim_id"],
    policy_id=fixture["policy_id"],
    run_dir=run_dir,
    policies=policies,
    clarification_responses=fixture.get("clarification_responses", {}),
)
executor = make_executor(session)

# Script: 5 tool_use turns then end_turn. Mirrors a real routed claim lifecycle.
scripted = [
    FakeResponse(content=[FakeBlock(type="tool_use", id="tu_1", name="lookup_policy", input={"policy_id": fixture["policy_id"]})], stop_reason="tool_use", usage=FakeUsage(100, 20)),
    FakeResponse(content=[FakeBlock(type="tool_use", id="tu_2", name="record_claim_fact", input={"field": "incident_date", "value": "2026-04-28"})], stop_reason="tool_use", usage=FakeUsage(120, 15)),
    FakeResponse(content=[FakeBlock(type="tool_use", id="tu_3", name="classify_claim", input={"claim_type": "property_damage", "confidence": 0.9, "rationale": "kitchen fire with property damage"})], stop_reason="tool_use", usage=FakeUsage(130, 25)),
    FakeResponse(content=[FakeBlock(type="tool_use", id="tu_4", name="assess_severity", input={"severity": "high", "rationale": "major kitchen damage"})], stop_reason="tool_use", usage=FakeUsage(140, 20)),
    FakeResponse(content=[FakeBlock(type="tool_use", id="tu_5", name="route_to_adjuster", input={"queue": "property_damage", "claim_summary": "Kitchen fire caused major property damage; routed to property queue."})], stop_reason="tool_use", usage=FakeUsage(150, 30)),
    FakeResponse(content=[FakeBlock(type="text", text="Claim routed.")], stop_reason="end_turn", usage=FakeUsage(160, 10)),
]
client = FakeClient(messages=FakeMessages(scripted=scripted))
trace_path = run_dir / "traces" / f"{fixture['claim_id']}.jsonl"

with Tracer(trace_path) as tracer:
    state = run_loop(
        client=client, model="offline-fake", system="test",
        tools=TOOL_SCHEMAS,
        messages=[{"role": "user", "content": fixture["initial_message"]}],
        tool_executor=executor, budget=Budget(max_input_tokens=1_000_000, max_wall_clock_s=60.0),
        tracer=tracer,
    )

print(f"claim_id: {session.claim_id}")
print(f"outcome: {session.outcome}")
print(f"routing: {json.dumps(session.routing)}")
print(f"turns: {state.turn_count} input={state.total_input_tokens} output={state.total_output_tokens}")
print("--- trace (stop_reason per turn) ---")
for line in trace_path.read_text().splitlines():
    ev = json.loads(line)
    calls = [(c["name"], c["input"]) for c in ev["tool_calls"]]
    print(f"turn {ev['turn']}: stop_reason={ev['stop_reason']} tools={calls}")
print(f"--- trace file: {trace_path} ---")
print(f"CONTINUED on tool_use x5, TERMINATED on end_turn at turn {state.turn_count}")
