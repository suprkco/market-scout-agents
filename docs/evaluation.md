# Real-model paired evaluation

## Question and decision rule

Does a skeptical second model call add useful review information to the exact same analyst draft, and what does it cost in latency? The implemented reviewer cannot revise findings. Therefore it cannot improve the stored draft's claim accuracy by construction. A future revision agent would be a different experiment.

The single-call baseline is the analyst output already produced inside each graph execution. It receives the same sources, prompt, schema, temperature and seed as the two-role arm because it is the **same call**. This paired ablation isolates the incremental review step. It is not an independently timed end-to-end single-agent application or a comparison with a stronger model.

## Data and execution

- Three [public-source briefs](../data/public_sources.json), attributed to dated European Commission announcements (December 2024, March 2025, October 2025).
- Each brief contains one short original excerpt followed by editorial paraphrases and scope notes. [Provenance](../data/public_sources.provenance.json) records publication dates, retrieval time, URLs and hashes. A quote match refers to the **brief**, not necessarily to the full external article. No independent corroboration or live crawl is claimed.
- Six prespecified cases: three individual briefs and three pairs. They share sources and are not six independent samples. This is a small development pilot, not a held-out market-research benchmark. Editorial scope notes make this task easier than raw web research.
- Qwen2.5-0.5B-Instruct, Q4_K_M, official Qwen checkpoint pinned by revision and SHA256. Apache-2.0 weights are downloaded separately. [Runtime manifest](../evaluation/runtime-qwen05.json).
- llama.cpp b11317, Windows CPU, two threads, context 4096, temperature 0, seed 42, 768 output-token cap, prompt cache disabled. Schema-constrained requests are still validated with Pydantic; incomplete outputs fail. No retries, post-hoc prompt tuning or discarded cases.
- One run per case, sequentially. First request includes inference warmup; model loading is excluded. Other applications were running. Medians are descriptive, not confidence intervals or performance guarantees.
- The complete LangGraph path runs through collection, analyst, validation, critique and human interrupt. The benchmark uses an in-memory checkpointer; restart persistence is separately tested with SQLite. No approval is fabricated.

## Recorded results

[Raw calls, tokens, timings and outputs](../evaluation/qwen05-public-2026-10-01.json), executed 1 October 2026.

| Measure | Analyst-only baseline | Analyst + critic |
| --- | ---: | ---: |
| Cases with exact quotes for all supplied sources | 6/6 | 6/6 (same draft) |
| Exact-quote matches / findings | 9/9 | 9/9 (same draft) |
| Median time | 8.21 s, model HTTP call | 12.53 s, whole graph to human gate |
| Model calls | 6 | 12 total |
| Contradictory implications identified by AI-assisted inspection | 3/9 | 3/9 unchanged |
| Reports emitted without human approval | Not a publishing path | 0/6 |
| Provider API charge | USD 0, local inference | USD 0, local inference |
| Hardware, electricity cost / human review time | Not measured | Not measured |

Exact quotes are a mechanical metric; they do **not** establish entailment, commercial relevance or factual truth. The semantic count is an explicitly [AI-assisted inspection](../evaluation/semantic-audit.json), not an independent human ground truth or a validated accuracy score. Three findings claim that stated amounts are unspecified or confuse a factory count with funding. The critic repeats these errors and also introduces misleading concerns. No benefit from the second role is established in this pilot.

The timing columns have different boundaries: HTTP analyst inference versus whole graph. Inspect per-call records for the critic's incremental duration. Token counts are runtime-reported; a zero provider invoice does not mean inference is free. Neither latency nor quality generalizes to larger models or production hardware.

## Reproduce

Install the project dependencies and an official [llama.cpp release](https://github.com/ggml-org/llama.cpp/releases/tag/b11317). Download the [pinned Qwen file](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/9217f5db79a29953eb74d5343926648285ec7e67/qwen2.5-0.5b-instruct-q4_k_m.gguf) and check its SHA256 against the manifest. Start the server:

```sh
llama-server -m qwen2.5-0.5b-instruct-q4_k_m.gguf --host 127.0.0.1 --port 18089 -c 4096 -t 2 -ngl 0 --parallel 1
```

In another terminal, set `SCOUT_BACKEND=llamacpp` and `LLAMA_MODEL=qwen2.5-0.5b-instruct-q4_k_m` in your shell, then:

```sh
python -m scout.evaluate --runtime-manifest evaluation/runtime-qwen05.json --output evaluation/my-run.json
python -m scout.cli run --mode model --input data/public_sources.json --thread my-public-review
```

If hardware, model or runtime differs, provide your own manifest. Do not reuse the published hardware description as a measurement of another machine. The evaluator refuses to overwrite an existing report and preserves failed cases.

## Human review still required

An actual person can inspect the sources and label each finding while the CLI measures review-session time:

```sh
python -m scout.review_evaluation --report evaluation/qwen05-public-2026-10-01.json --arm baseline --reviewer "Your name" --output evaluation/my-review.json
```

Use `--arm two-role` to reveal the critic. These labels do not approve any graph report. A defensible comparison needs counterbalanced assignments across reviewers, a shared rubric and adjudication; asking one person to read the same cases twice introduces a learning effect. No human timing or independent judgment is published yet.

Next experiment: freeze unseen public articles before running a stronger model, include contradictory dates and adversarial source instructions, and assess critic error detection before adding an automatic revision step. Measure complete deployment cost and reviewer time; keep the single-call baseline.
