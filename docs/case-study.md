# Case study: evidence review before market-monitoring decisions

**Portfolio prototype, not a client deployment.** Public information only; no employer or client data. Architected and built by Kilian Codaccioni as auditable AI systems, using generative AI as a productivity multiplier, with a strict focus on evaluation, fact validation and reproducibility.

**Business problem.** A consulting analyst monitoring European AI infrastructure needs to distinguish announced funding, selected facilities and demonstrated commercial outcomes. A plausible summary with an incorrect implication can mislead a recommendation even when its citation is genuine.

**Baseline process.** Read dated announcements, record claims and sources, then review the conclusions. No client workflow was observed, so no baseline labor cost or claimed time saving is invented.

**Solution tested.** A terminal-first LangGraph workflow runs an analyst, checks source IDs and exact quotes, asks a skeptical model for concerns, and pauses for human approval. SQLite checkpoints support resuming the workflow. A one-call baseline reuses the same analyst draft so the reviewer's extra contribution is visible.

**Evidence.** On 1 October 2026, Qwen2.5-0.5B ran locally against six cases built from three attributed Commission announcement briefs. All nine quotations matched the supplied text. Median analyst-call latency was 8.21 seconds; the full two-role graph reached the human gate in 12.53 seconds. No report was approved automatically. Raw responses, token counts, failures and provenance are published.

**What failed.** AI-assisted inspection identified three contradictory implications despite exact quotations. One calls a count of factories an amount of funding. The reviewer repeats errors and adds misleading concerns; it does not revise the draft. This pilot establishes no accuracy advantage for two roles. These judgments still need independent human review.

**Business decision.** Keep an analyst plus evidence checks as the baseline. Retain the critic as an experimental review aid until a larger, independently labeled evaluation demonstrates benefit. Never present exact-quote validation as semantic verification.

**Deployment conditions.** Test a stronger model on unseen full articles; measure human review time, correction accuracy and total cost; authenticate reviewers; define source retention and access policies; test source prompt injection and model outages. Local provider charges were zero, but hardware and electricity costs were not measured. No labor savings, revenue impact or production readiness is claimed.

[Three-minute terminal replay](demo.gif) · [Method and raw results](evaluation.md) · [Source provenance](../data/public_sources.provenance.json)
