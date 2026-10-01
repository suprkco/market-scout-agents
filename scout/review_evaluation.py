"""Time an actual person's evidence review; never approve the workflow."""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from scout.cli import render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True)
    parser.add_argument('--sources', default='data/public_sources.json')
    parser.add_argument('--arm', choices=['baseline', 'two-role'], required=True)
    parser.add_argument('--reviewer', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error('Output exists; choose a new filename')
    raw = Path(args.report).read_bytes()
    sources_raw = Path(args.sources).read_bytes().replace(b'\r\n', b'\n')
    report = json.loads(raw)
    if hashlib.sha256(sources_raw).hexdigest() != report['sources_sha256']:
        parser.error('Sources differ from the evaluated corpus')
    sources = {s['id']: s for s in json.loads(sources_raw)}
    result = {'reviewer': args.reviewer, 'arm': args.arm,
              'report_sha256': hashlib.sha256(raw).hexdigest(),
              'started_at': datetime.now(timezone.utc).isoformat(), 'rows': [],
              'scope': 'Self-reported human judgments, measured active session wall time; not workflow approval.'}
    for row in report['rows']:
        input(f"Press Enter to start reviewing {row['case']} (timer starts afterwards). ")
        start = time.perf_counter()
        for sid in row['source_ids']:
            s = sources[sid]
            print(render({'findings': [{'headline': s['title'], 'source_id': sid,
                                       'quote': s['text'], 'implication': 'Supplied brief: ' + s['url']}]}))
        visible = {'findings': row['findings']}
        if args.arm == 'two-role':
            visible['concerns'] = row['concerns']
        print(render(visible))
        labels = []
        for i, _ in enumerate(row['findings']):
            label = ''
            while label not in {'supported', 'contradicted', 'unclear'}:
                label = input(f'Finding {i+1}, including its implication [supported/contradicted/unclear]: ').strip()
            labels.append(label)
        note = input('Explain any incorrect claim or misleading critique: ')
        result['rows'].append({'case': row['case'], 'labels': labels, 'note': note,
                               'review_seconds': time.perf_counter() - start})
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(f'Review saved to {output}; no report approved or published.')


if __name__ == '__main__':
    main()
