# Capstone Completion Report

Date (UTC): 2026-09-27 · OS: Windows (win32) · Python 3.12.4 · API spend: $0.00 (no key available; nothing fabricated)

## System 1 — Agentic Loop

- Verification command: `python -m pytest tests/ -v` in `Build a Claims Intake Agent with a stop_reason-Driven Loop/exercises/03-dynamic-decomposition/solution` (own `.venv`, `anthropic==0.39.0`)
- Actual test result: 29 collected, 29 passed, 0 failed, 0 skipped, exit 0 (`system-1-agentic-loop/test-output.txt`)
- Run artifact: live `python -m claims_intake.run --all` could not run — `RuntimeError: ANTHROPIC_API_KEY is not set`, exit 1 (`system-1-agentic-loop/run-output.txt`)
- stop_reason evidence: offline single-claim run through the real `claims_intake/loop.py::run` + real `make_executor` with scripted `FakeClient` — `trace-claim_01_kitchen_fire.jsonl` shows turns 1–5 `stop_reason=tool_use` (lookup_policy → record_claim_fact → classify_claim → assess_severity → route_to_adjuster) and turn 6 `stop_reason=end_turn`; human-readable in `offline-trace.txt`
- Routing/escalation evidence: offline claim terminated `outcome=routed` (`claim_type=property_damage`, `severity=high`, `confidence=0.9`); 8-claim live distribution (7 routed / 1 escalated) not executed — recorded as blocker, not claimed

## System 2 — Context Strategy

- Verification command: `python -m pytest tests/ -v` in `Engineer a Long-Conversation Context Strategy for a Retail Support Copilot/04-assemble-and-locate/solution` (own `.venv`, `anthropic==0.69.0`)
- Actual test result: 30 collected, 28 passed, 0 failed, 2 skipped (skips require live `run --build` artifacts), exit 0 (`system-2-context-strategy/test-output.txt`)
- Baseline tokens: 47144 (heuristic `len/3.8`, no API key) — printed by the failed `--build` attempt and reproduced offline
- Assembled tokens: no live assembly (case-facts LLM call failed: no API key; CLI fallback hit Windows `WinError 206`). Deterministic offline sections match the reference exactly: `case_facts` 149, `active` 19538 byte-exact; pruner 57 fields → 5, 532 → 45 tokens (`offline-measurements.txt`)
- Reduction: synthetic-placeholder assembly 58.09% (mechanism demo only — explicitly not the eval artifact); reference 20,350 / 56.83% quoted from solution README, not claimed as this run
- Evaluation result: not executed (needs LLM); 6 questions preserved in `eval_questions.json`
- Control regression: not executed; design documented in `architecture-notes.txt` (Q6 `in_progress` is the strict case-facts-only token per reference run)

## System 3 — Claude Code

- Verification command: `python -m pytest tests/ -v` + `python -m ecommerce_team_config .` in `Configure Claude Code for a Multi-Surface Monorepo Team/04-plan-mode-and-explore-decision-doc/solution` (own `.venv`)
- Actual test result: 35 passed, exit 0 (`system-3-claude-code/test-output.txt`)
- Validator result: `OK`, exit 0 (`system-3-claude-code/validator-output.txt`)
- CLAUDE.md evidence: `config/CLAUDE.md` (project-level entry point, scope table, 4 `@.claude/standards/` imports)
- Rules evidence: `config/.claude/rules/{react,api,tests}.md` with `paths` glob frontmatter (quoted in `architecture-notes.txt`)
- Command evidence: `config/.claude/commands/review.md` (project-scoped, read-oriented allowlist, interview pattern)
- Skill evidence: `config/.claude/skills/deploy-check/SKILL.md` (`context: fork`, read-only `allowed-tools`, 3 checks, personalization note) + `config/plan-mode-vs-direct-execution.md`

## System 4 — Orchestrator

- Verification command: `python -m pytest tests/ -v` in `Build a Multi-Shift Quality Monitoring System with Claude Orchestration/04-fork-scratchpad/solution` (dedicated venv at short path `C:/Users/Prakhar/AppData/Local/Temp/opencode/s4venv`, same pinned deps — in-tree venv hit Windows MAX_PATH)
- Actual test result: 33 collected, 33 passed, exit 0 (`system-4-orchestrator/test-output.txt`)
- SQL-filter evidence: warm tier 40 defects → indexed `defects_since` slice of 17 rows since `2026-04-01T00:00:00Z` (`EXPLAIN: SEARCH defects USING INDEX idx_defects_ts`); run printed `shift C: 17 new defects` (`run-output.txt`)
- Hot-state size: 980 bytes (`state-size.txt`, copy `hot_state.json`) — under ~5 KB
- Crash recovery: `fork-recovery-demo.txt` — 10-min-old partial → `resume`, 60-min-old → `fresh`, complete → `fresh`; threshold `STALE_RESUME_THRESHOLD_MINUTES = 30` (`recovery.py`)
- Fork evidence: `data/forks/lot-2026-0430-B-dielectric` + `data/forks/bank-C-7-calibration-drift`, each with isolated `scratchpad.jsonl`; base `hot_state.json` untouched (980 bytes); merged main scratchpad now 3 lines (`shift_scratchpad.jsonl` copy)

## Reflection

- Reflection path: `capstone-evidence/final/reflection-brief.md` (all 20 questions answered, every answer cites run artifacts; no placeholders; no secrets)
- Checklist status: `capstone-evidence/final/rubric-checklist.md` — System 3 fully checked; System 4 fully checked; System 1 checked except live 8-claim termination; System 2 live-eval boxes honestly unchecked (blocked, documented)

## Problems encountered

1. No `ANTHROPIC_API_KEY` in environment — Systems 1/2 live runs and System 2 evals blocked. Resolved by recording the exact failures and capturing offline evidence through real code paths (S1 real loop + scripted client; S2 deterministic pruner/transcript/assembler measurements). Nothing fabricated.
2. System 4 `pip install` failed with Windows MAX_PATH (`OSError: [Errno 2]` on a long `anthropic` filename). Resolved with a dedicated venv at a short path (`...\Temp\opencode\s4venv`); identical pinned dependencies; 33/33 pass.
3. System 2 CLI fallback crashed with Windows `WinError 206` (47k-token prompt passed as process argv). Resolved by documenting it, removing the empty partial `runs/` dir so artifact-gated tests skip cleanly, and noting the stdin/temp-file fix as the Q20 proposal.
4. Default `python3` on this machine is 3.8 (below the `>=3.11` requirement); all venvs were built with the 3.12 interpreter. `python`/`pip` CWD quirks with space-bearing paths handled via explicit `workdir` / quoted paths.

## Final artifact tree

```
capstone-evidence/
├── execution-log.txt
├── system-1-agentic-loop/
│   ├── architecture-notes.txt
│   ├── offline-trace.txt
│   ├── offline_demo.py
│   ├── run-output.txt          (live --all attempt, exit 1, no key)
│   ├── test-output.txt         (29 passed)
│   └── trace-claim_01_kitchen_fire.jsonl
├── system-2-context-strategy/
│   ├── architecture-notes.txt
│   ├── eval_questions.json
│   ├── offline-measurements.txt
│   ├── offline_demo.py
│   ├── run-output.txt          (--build attempt: baseline 47144, then WinError 206)
│   └── test-output.txt         (28 passed, 2 skipped)
├── system-3-claude-code/
│   ├── architecture-notes.txt
│   ├── config/
│   │   ├── CLAUDE.md
│   │   ├── .claude/            (commands/review.md, rules/*.md, skills/deploy-check/SKILL.md, standards/*.md)
│   │   └── plan-mode-vs-direct-execution.md
│   ├── test-output.txt         (35 passed)
│   └── validator-output.txt    (OK, exit 0)
├── system-4-orchestrator/
│   ├── architecture-notes.txt
│   ├── fork-recovery-demo.txt
│   ├── hot_state.json          (980 bytes)
│   ├── manifest.jsonl
│   ├── recorded-response.json
│   ├── run-output.txt          (shift C, 17 new defects, exit 0)
│   ├── shift_scratchpad.jsonl
│   ├── state-size.txt          (980)
│   └── test-output.txt         (33 passed)
└── final/
    ├── FINAL-REPORT.md         (this file)
    ├── reflection-brief.md
    ├── rubric-checklist.md
    └── test-summary.txt
```

Remaining blockers (no fabrication): live 8-claim intake run + live context build/6-eval/control require `ANTHROPIC_API_KEY` (and, for the CLI fallback on Windows, a stdin-based prompt handoff). Everything runnable offline is green: 29 + 28 (+2 skipped) + 35 + 33 tests, validator OK, offline shift exit 0.
