# Three-minute terminal replay

Ten 18-second slides. Edited presentation timing, recorded inference outputs; no narrated video or live speed claim.

Rebuild with `python scripts/build-demo.py` after installing Pillow.

## 000-018 seconds: 01 / the consulting question

market scout / evidence before decisions

What changed in European AI infrastructure?
Which conclusions can an analyst defend?

Real local model. Public, dated source briefs.
Edited playback of recorded results; not real-time inference.
No client data. No automatic publication.

## 018-036 seconds: 02 / the evidence

$ inspect data/public_sources.json

2024-12-10  First AI Factory selection
2025-03-12  Second AI Factory selection
2025-10-10  Third AI Factory selection

Publisher: European Commission / DG CONNECT
Short excerpts + editorial paraphrases, not full articles.
URLs, retrieval dates and hashes are committed.

## 036-054 seconds: 03 / the experiment

$ python -m scout.evaluate [recorded run]

Qwen2.5-0.5B-Instruct / Q4_K_M / CPU
Six cases, three shared sources, one run per case.
Baseline: the same analyst call, without the critic.
Treatment: analyst -> quote check -> critic -> human gate.

This is a small development pilot, not a held-out benchmark.

## 054-072 seconds: 04 / observed execution

first-wave: 9.20s / awaiting human review
second-wave: 10.63s / awaiting human review
third-wave: 9.95s / awaiting human review
first-and-second: 15.89s / awaiting human review
second-and-third: 14.43s / awaiting human review
first-and-third: 18.54s / awaiting human review

12 model calls. No discarded cases or retries.
Raw model outputs and token usage are available.

## 072-090 seconds: 05 / exact citations

Exact quotations: 9/9
Coverage: 9/9 supplied source appearances

A matching quotation does not prove the implication.

The next screen shows an actual failure.
Inspect the quote and implication together.

## 090-108 seconds: 06 / an actual contradiction

Quote excerpt from supplied brief:
The first AI Factories will represent a €1.5 billion investment, combining national and EU funding.

Model implication:
The €1.5 billion investment is described as a combined national and EU funding, but the actual amount is not specified.

AI-assisted audit: the amount IS specified.
Independent human annotation is still pending.

## 108-126 seconds: 07 / did the critic help?

Recorded critic concern:
The €1.5 billion investment is described as a combined national and EU funding, but the actual amount is not specified.

It repeats the incorrect implication.
The critic cannot edit the draft in this architecture.
Inspection found 3 contradictory findings out of 9.
No demonstrated accuracy gain from the second role.

## 126-144 seconds: 08 / latency and cost

Analyst HTTP call, median: 8.21 s
Whole graph to human gate, median: 12.53 s

Different timing boundaries; raw per-call timings retained.
Provider charge: USD 0 (local model)
Hardware / electricity cost: not measured
Human review time: not measured
A zero API invoice does not mean free operation.

## 144-162 seconds: 09 / the human boundary

$ python -m scout.cli run --mode model [recorded]

scout / awaiting_review
Thread: public-demo-oct01
Findings: 3
Approval required before creating an approved local report.

No human approval was simulated.
Review labels and session timing have a separate CLI.

## 162-180 seconds: 10 / the recommendation

Keep the single-call analyst as the baseline.
Do not confuse exact quotes with correct conclusions.
Evaluate the critic before relying on it.

Next: independent human labels, stronger model, unseen articles.
Then measure reviewer time and deployment cost.

github.com/suprkco/market-scout-agents
Method, raw outputs, case study and tests are in the repo.
