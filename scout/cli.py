import argparse
import json
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from scout.graph import build_graph


def render(report):
    lines = ['scout / ' + report.get('status', 'report')]
    review = report.get('review', report)
    for finding in review.get('findings', []):
        lines.extend(['', finding['headline'], '  Source: ' + finding['source_id'],
                      '  Quote: ' + finding['quote'], '  Implication: ' + finding['implication']])
    for concern in review.get('concerns', []):
        lines.append('! ' + concern)
    if 'decision' in report:
        lines.extend(['Reviewer: ' + report['decision']['reviewer'], 'Note: ' + report['decision']['note']])
    if report.get('status') == 'awaiting_review':
        lines.extend(['', 'Thread: ' + report['thread'], 'Resume with approve or reject, the same --thread and --db, plus --reviewer and --note.'])
    return ''.join(c if c.isprintable() or c == '\n' else ' ' for c in '\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description='Research, review, then create a local report. Never publishes externally.')
    parser.add_argument('action', choices=['run', 'approve', 'reject'])
    parser.add_argument('--thread', required=True)
    parser.add_argument('--db', default='checkpoints.db')
    parser.add_argument('--input', default='data/synthetic_sources.json')
    parser.add_argument('--mode', choices=['fixture', 'ollama'], default='fixture')
    parser.add_argument('--reviewer')
    parser.add_argument('--note')
    parser.add_argument('--json', action='store_true', help='Emit the full machine-readable report')
    args = parser.parse_args()
    config = {'configurable': {'thread_id': args.thread}}
    with SqliteSaver.from_conn_string(args.db) as saver:
        graph = build_graph(saver)
        snapshot = graph.get_state(config)
        if args.action == 'run':
            if snapshot.values:
                parser.error('Thread already exists; use a new thread ID or review the pending run')
            if Path(args.input).stat().st_size > 300_000:
                parser.error('Input exceeds 300 KB')
            sources = json.loads(Path(args.input).read_text(encoding='utf-8'))
            result = graph.invoke({'sources': sources, 'mode': args.mode}, config)
        else:
            if not args.reviewer or not args.note:
                parser.error('Review requires --reviewer and --note')
            if not snapshot.next or 'review' not in snapshot.next:
                parser.error('No pending human review for this thread')
            result = graph.invoke(Command(resume={'approved': args.action == 'approve', 'reviewer': args.reviewer, 'note': args.note}), config)
        if '__interrupt__' in result:
            report = {'status': 'awaiting_review', 'thread': args.thread, 'review': result['__interrupt__'][0].value}
        else:
            report = result['report']
        print(json.dumps(report, indent=2) if args.json else render(report))

if __name__ == '__main__':
    main()
