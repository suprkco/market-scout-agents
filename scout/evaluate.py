"""Paired analyst ablation: the second role critiques the same frozen draft."""
import argparse
import hashlib
import json
import os
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from langgraph.checkpoint.memory import InMemorySaver

from scout.graph import build_graph
from scout.inference import capture_calls


def evidence_scores(findings, sources):
    lookup = {s['id']: s['text'] for s in sources}
    valid = [f for f in findings if f['source_id'] in lookup
             and f['quote'] in lookup[f['source_id']]]
    return {'findings': len(findings), 'exact_quote_matches': len(valid),
            'covered_sources': len({f['source_id'] for f in valid}),
            'supplied_sources': len(sources)}


def run_case(case, sources):
    selected = [s for s in sources if s['id'] in case['source_ids']]
    if len(selected) != len(case['source_ids']):
        raise ValueError('Case contains an unknown or duplicate source')
    config = {'configurable': {'thread_id': case['id']}}
    graph = build_graph(InMemorySaver())
    started = time.perf_counter()
    error = None
    with capture_calls() as calls:
        try:
            graph.invoke({'sources': selected, 'mode': 'model'}, config)
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc)[:300]}
    elapsed = time.perf_counter() - started
    state = graph.get_state(config)
    findings = state.values.get('findings', [])
    analyst = next((c for c in calls if c['schema'] == 'Findings'), None)
    critic = next((c for c in calls if c['schema'] == 'Critique'), None)
    return {'case': case['id'], 'source_ids': case['source_ids'], 'calls': calls,
            'findings': findings, 'concerns': state.values.get('concerns', []),
            'scores': evidence_scores(findings, selected),
            'single_call_seconds': analyst['wall_seconds'] if analyst else None,
            'critic_added_seconds': critic['wall_seconds'] if critic else None,
            'pipeline_seconds': elapsed,
            'awaiting_human_review': state.next == ('review',),
            'report_emitted': 'report' in state.values, 'error': error}


def summarize(rows):
    single_times = [r['single_call_seconds'] for r in rows if r['single_call_seconds'] is not None]
    return {'cases': len(rows),
            'completed_to_human_gate': sum(r['awaiting_human_review'] for r in rows),
            'failed_cases': sum(r['error'] is not None for r in rows),
            'reports_emitted_without_human': sum(r['report_emitted'] for r in rows),
            'findings': sum(r['scores']['findings'] for r in rows),
            'exact_quote_matches': sum(r['scores']['exact_quote_matches'] for r in rows),
            'covered_sources': sum(r['scores']['covered_sources'] for r in rows),
            'supplied_sources': sum(r['scores']['supplied_sources'] for r in rows),
            'single_call_median_seconds': statistics.median(single_times) if single_times else None,
            'pipeline_median_seconds': statistics.median(r['pipeline_seconds'] for r in rows),
            'human_review_seconds': None, 'semantic_accuracy': None,
            'provider_charge_usd': 0, 'electricity_and_hardware_cost_usd': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', default='data/public_sources.json')
    parser.add_argument('--cases', default='data/evaluation_cases.json')
    parser.add_argument('--output', default='evaluation/local-model.json')
    parser.add_argument('--runtime-manifest', required=True,
                        help='JSON with checkpoint hash and runtime launch/version details')
    args = parser.parse_args()
    backend = os.getenv('SCOUT_BACKEND', 'ollama')
    endpoint = os.getenv('LLAMA_URL', 'http://127.0.0.1:18089') if backend == 'llamacpp' else os.getenv('OLLAMA_URL', 'http://localhost:11434')
    if urlsplit(endpoint).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        parser.error('This zero-provider-charge protocol only supports a local model endpoint')
    output = Path(args.output)
    if output.exists():
        parser.error('Output exists; use a new filename to preserve previous measurements')
    source_bytes = Path(args.sources).read_bytes().replace(b'\r\n', b'\n')
    case_bytes = Path(args.cases).read_bytes().replace(b'\r\n', b'\n')
    sources, cases = json.loads(source_bytes), json.loads(case_bytes)
    if not cases or len({c['id'] for c in cases}) != len(cases):
        parser.error('Expected nonempty uniquely identified cases')
    report = {'started_at': datetime.now(timezone.utc).isoformat(),
              'hash_policy': 'UTF-8 bytes with CRLF normalized to LF for cross-platform checkouts',
              'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                              'processor': platform.processor()},
              'runtime': json.loads(Path(args.runtime_manifest).read_text(encoding='utf-8')),
              'sources_sha256': hashlib.sha256(source_bytes).hexdigest(),
              'cases_sha256': hashlib.sha256(case_bytes).hexdigest(),
              'protocol': 'One run per case, no retry or tuning between cases. Paired ablation reuses the exact analyst draft as the single-call baseline. Critic cannot revise claims. HTTP wall times include inference; startup is excluded. No human approval is simulated.',
              'rows': []}
    output.parent.mkdir(parents=True, exist_ok=True)
    for case in cases:
        row = run_case(case, sources)
        report['rows'].append(row)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        print(f"{case['id']}: {row['pipeline_seconds']:.2f}s; gate={row['awaiting_human_review']}; error={row['error']}", flush=True)
    report['summary'] = summarize(report['rows'])
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
