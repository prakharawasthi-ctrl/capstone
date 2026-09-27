# Rubric checklist — checked only where evidence exists (2026-09-27 run)

## Agentic loop (System 1)
- [x] test suite passes — `system-1-agentic-loop/test-output.txt`: 29 passed, exit 0
- [x] end-to-end claims run captured — OFFLINE single-claim run via real `loop.run` + scripted model: `offline-trace.txt` + `trace-claim_01_kitchen_fire.jsonl` (6 turns, outcome=routed). NOTE: live 8-claim `run --all` blocked (no ANTHROPIC_API_KEY); see `run-output.txt` (exit 1).
- [ ] each claim terminates in routing or escalation — NOT demonstrated live (8-claim run blocked); single offline claim terminated routed. Fixture metadata targets 7 routed/1 escalated per `test_fixture_outcome_distribution_meets_targets`, but that is not a run.
- [x] `stop_reason=tool_use` evidence captured — `trace-claim_01_kitchen_fire.jsonl` turns 1–5
- [x] `stop_reason=end_turn` evidence captured — same trace, turn 6
- [x] exact loop file identified — `architecture-notes.txt`: `claims_intake/loop.py`
- [x] exact loop function identified — `architecture-notes.txt`: `run(...)`
- [x] anti-pattern identified — `architecture-notes.txt` (4 AST audits in `tests/test_antipatterns.py`)

## Context strategy (System 2)
- [x] test suite passes — `system-2-context-strategy/test-output.txt`: 28 passed, 2 skipped, exit 0 (skips require live `run --build` artifacts)
- [ ] budget artifact exists — NO live `budget.json` (live `--build` failed: no API key; CLI fallback hit WinError 206). Reference `runs/20260519-124910/budget.json` numbers are NOT claimed.
- [ ] assembled context at least 50% smaller than baseline — NOT demonstrated with real LLM summaries (synthetic-placeholder assembly reached 58.09% but is explicitly not the eval artifact; see `offline-measurements.txt`)
- [ ] 6 evaluation questions recorded — NOT executed (needs LLM)
- [ ] at least 5/6 answered — NOT executed
- [ ] control variant recorded — NOT executed
- [ ] regression recorded — NOT executed
- [x] actual token numbers documented — deterministic subset only: baseline 47144, active 19538, case_facts 149, pruner 532→45 (`offline-measurements.txt`); these match the README reference values for the non-LLM sections
- [x] preserved-vs-summarized information identified — `architecture-notes.txt` (active verbatim vs resolved summaries)

## Claude Code configuration (System 3)
- [x] validator succeeds — `system-3-claude-code/validator-output.txt`: OK
- [x] exit code 0 — recorded in `validator-output.txt` (VALIDATOR_EXIT=0)
- [x] test suite passes — `system-3-claude-code/test-output.txt`: 35 passed
- [x] CLAUDE.md exists — `config/CLAUDE.md`
- [x] `@import` demonstrated — 4 `@.claude/standards/*.md` lines in `config/CLAUDE.md`
- [x] path-scoped rules exist — `config/.claude/rules/{react,api,tests}.md`
- [x] glob/path frontmatter exists — quoted in `architecture-notes.txt`
- [x] slash command exists — `config/.claude/commands/review.md`
- [x] skill exists — `config/.claude/skills/deploy-check/SKILL.md`
- [x] `context: fork` — in SKILL.md frontmatter (quoted in notes)
- [x] read-only allowed-tools — Read/Grep/Glob + git/gh read-only Bash patterns (quoted in notes)
- [x] plan/explore decision document — `config/plan-mode-vs-direct-execution.md`

## Layer 3 orchestration (System 4)
- [x] test suite passes — `system-4-orchestrator/test-output.txt`: 33 passed
- [x] shift run captured — `run-output.txt`: shift C, 17 new defects, exit 0
- [x] SQL-filtered defect slice demonstrated — 17 of 40 via indexed `defects_since` (EXPLAIN shows index use; evidence in notes + demo commands)
- [x] hot-state size measured — `state-size.txt`: 980
- [x] hot state under ~5 KB — 980 bytes < ~5 KB
- [x] crash recovery demonstrated — `fork-recovery-demo.txt`: resume/fresh decisions
- [x] staleness threshold identified — 30 min (`recovery.py::STALE_RESUME_THRESHOLD_MINUTES`)
- [x] resume/fresh decision explained — `architecture-notes.txt`
- [x] forked investigation demonstrated — two forks under `data/forks/` (see demo output)
- [x] scratchpads isolated — per-fork `scratchpad.jsonl` (1 entry each), base untouched, merged to 3-line main scratchpad
