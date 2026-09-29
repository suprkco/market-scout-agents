# Five-minute interview walkthrough

1. Start a run with a fresh `--thread` value. Show that output is `awaiting_review`, not an approved report.
2. Close the process. Resume the same thread from a new invocation, demonstrating SQLite persistence.
3. Reject it with a reviewer name and note. Show the rejection record without approved findings.
4. Inspect the analyst/reviewer nodes and the exact-quote validator. Explain that fixture mode is deterministic, while Ollama mode performs two model calls.
5. Discuss limitations: a correct quote can accompany a wrong inference; self-reported reviewer identity is not authentication; real monitoring needs dated inputs and independent corroboration.

Never present the fictional company examples as real market intelligence. Describe this as an AI-assisted workflow prototype with measured control-flow behavior, not an evaluated autonomous research team.
