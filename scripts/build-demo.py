"""Build a three-minute edited terminal replay from committed experiment outputs.

Optional dependency: Pillow. This renders text, not an invented inference run.
"""
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / 'evaluation/qwen05-public-2026-10-01.json').read_text(encoding='utf-8'))
demo = json.loads((ROOT / 'docs/demo-public-pending.json').read_text(encoding='utf-8'))
summary = report['summary']
bad = next(r for r in report['rows'] if r['case'] == 'first-and-second')
slides = [
    ('01 / the consulting question', ['market scout / evidence before decisions', '',
     'What changed in European AI infrastructure?',
     'Which conclusions can an analyst defend?', '',
     'Real local model. Public, dated source briefs.',
     'Edited playback of recorded results; not real-time inference.',
     'No client data. No automatic publication.']),
    ('02 / the evidence', ['$ inspect data/public_sources.json', '',
     '2024-12-10  First AI Factory selection',
     '2025-03-12  Second AI Factory selection',
     '2025-10-10  Third AI Factory selection', '',
     'Publisher: European Commission / DG CONNECT',
     'Short excerpts + editorial paraphrases, not full articles.',
     'URLs, retrieval dates and hashes are committed.']),
    ('03 / the experiment', ['$ python -m scout.evaluate [recorded run]', '',
     'Qwen2.5-0.5B-Instruct / Q4_K_M / CPU',
     'Six cases, three shared sources, one run per case.',
     'Baseline: the same analyst call, without the critic.',
     'Treatment: analyst -> quote check -> critic -> human gate.', '',
     'This is a small development pilot, not a held-out benchmark.']),
    ('04 / observed execution', [r['case'] + f": {r['pipeline_seconds']:.2f}s / awaiting human review" for r in report['rows']] + ['',
     '12 model calls. No discarded cases or retries.',
     'Raw model outputs and token usage are available.']),
    ('05 / exact citations', [f"Exact quotations: {summary['exact_quote_matches']}/{summary['findings']}",
     'Coverage: 9/9 supplied source appearances', '',
     'A matching quotation does not prove the implication.', '',
     'The next screen shows an actual failure.',
     'Inspect the quote and implication together.']),
    ('06 / an actual contradiction', ['Quote excerpt from supplied brief:',
     bad['findings'][0]['quote'].split('. ')[0] + '.', '',
     'Model implication:', bad['findings'][0]['implication'], '',
     'AI-assisted audit: the amount IS specified.',
     'Independent human annotation is still pending.']),
    ('07 / did the critic help?', ['Recorded critic concern:', bad['concerns'][0], '',
     'It repeats the incorrect implication.',
     'The critic cannot edit the draft in this architecture.',
     'Inspection found 3 contradictory findings out of 9.',
     'No demonstrated accuracy gain from the second role.']),
    ('08 / latency and cost', [f"Analyst HTTP call, median: {summary['single_call_median_seconds']:.2f} s",
     f"Whole graph to human gate, median: {summary['pipeline_median_seconds']:.2f} s", '',
     'Different timing boundaries; raw per-call timings retained.',
     'Provider charge: USD 0 (local model)',
     'Hardware / electricity cost: not measured',
     'Human review time: not measured',
     'A zero API invoice does not mean free operation.']),
    ('09 / the human boundary', ['$ python -m scout.cli run --mode model [recorded]', '',
     'scout / ' + demo['status'],
     'Thread: ' + demo['thread'],
     f"Findings: {len(demo['review']['findings'])}",
     'Approval required before creating an approved local report.', '',
     'No human approval was simulated.',
     'Review labels and session timing have a separate CLI.']),
    ('10 / the recommendation', ['Keep the single-call analyst as the baseline.',
     'Do not confuse exact quotes with correct conclusions.',
     'Evaluate the critic before relying on it.', '',
     'Next: independent human labels, stronger model, unseen articles.',
     'Then measure reviewer time and deployment cost.', '',
     'github.com/suprkco/market-scout-agents',
     'Method, raw outputs, case study and tests are in the repo.']),
]
font_candidates = ['C:/Windows/Fonts/consola.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
font_path = next((p for p in font_candidates if Path(p).exists()), None)
if font_path is None:
    raise SystemExit('Install Consolas or DejaVu Sans Mono to reproduce the render.')
font = ImageFont.truetype(font_path, 22)
frames = []
script = ['# Three-minute terminal replay', '',
          'Ten 18-second slides. Edited presentation timing, recorded inference outputs; no narrated video or live speed claim.', '',
          'Rebuild with `python scripts/build-demo.py` after installing Pillow.', '']
for i, (title, paragraphs) in enumerate(slides):
    im = Image.new('RGB', (1120, 620), '#101214')
    draw = ImageDraw.Draw(im)
    draw.text((30, 22), 'scout / ' + title, font=font, fill='#e7e7e7')
    draw.line((30, 61, 1090, 61), fill='#505050')
    lines = [line for p in paragraphs for line in (textwrap.wrap(p, width=78) or [''])]
    if len(lines) > 17:
        raise ValueError(f'Slide {i+1} would overflow: {len(lines)} lines')
    for j, line in enumerate(lines):
        draw.text((30, 85 + j*27), line, font=font, fill='#cdd3d8')
    draw.text((30, 575), f'Edited replay  |  {i*18:03d}-{(i+1)*18:03d}s / 180s  |  Real recorded outputs', font=font, fill='#929ca3')
    frames.append(im.convert('P', palette=Image.Palette.ADAPTIVE))
    script.extend([f'## {i*18:03d}-{(i+1)*18:03d} seconds: {title}', '', *paragraphs, ''])
frames[0].save(ROOT/'docs/demo.gif', save_all=True, append_images=frames[1:], duration=18000, loop=0, optimize=False)
(ROOT/'docs/demo-script.md').write_text('\n'.join(script).rstrip()+'\n', encoding='utf-8')
