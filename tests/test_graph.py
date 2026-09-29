import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from pydantic import ValidationError

from scout.graph import analyze, build_graph, collect, finalize, validate_evidence
from scout.models import Findings

SOURCES = json.loads(Path('data/synthetic_sources.json').read_text())
CONFIG = {'configurable': {'thread_id': 'test'}}

def test_must_pause_before_report():
    graph = build_graph(InMemorySaver())
    result = graph.invoke({'sources': SOURCES, 'mode': 'fixture'}, CONFIG)
    assert '__interrupt__' in result and 'report' not in result

@pytest.mark.parametrize('approved', [True, False])
def test_review_survives_restart(tmp_path, approved):
    path = str(tmp_path / 'checkpoints.db')
    with SqliteSaver.from_conn_string(path) as saver:
        build_graph(saver).invoke({'sources': SOURCES, 'mode': 'fixture'}, CONFIG)
    with SqliteSaver.from_conn_string(path) as saver:
        result = build_graph(saver).invoke(Command(resume={'approved': approved, 'reviewer': 'Demo reviewer', 'note': 'Synthetic fixture inspected'}), CONFIG)
    assert result['report']['status'] == ('approved' if approved else 'rejected')
    assert ('findings' in result['report']) == approved

def test_strings_cannot_approve():
    graph = build_graph(InMemorySaver())
    graph.invoke({'sources': SOURCES}, CONFIG)
    with pytest.raises(ValidationError):
        graph.invoke(Command(resume={'approved': 'yes', 'reviewer': 'Demo', 'note': 'test'}), CONFIG)

@pytest.mark.parametrize('change', ['quote', 'source'])
def test_fabricated_evidence_rejected(change):
    state = {'sources': SOURCES}
    state.update(analyze(state))
    state['findings'][0]['quote' if change == 'quote' else 'source_id'] = 'invented evidence identifier'
    with pytest.raises(ValueError):
        validate_evidence(state)

def test_duplicate_sources_rejected():
    with pytest.raises(ValueError):
        collect({'sources': [SOURCES[0], SOURCES[0]]})

def test_post_review_tampering_rejected():
    state = {'sources': SOURCES}
    state.update(analyze(state))
    state.update(validate_evidence(state))
    state['findings'][0]['implication'] = 'Changed after review'
    state['decision'] = {'approved': True}
    with pytest.raises(ValueError, match='changed'):
        finalize(state)

def test_llm_output_is_validated(monkeypatch):
    fake = Findings(findings=[{'headline': 'Fabricated', 'category': 'other', 'source_id': 'unknown', 'quote': 'This passage was never provided.', 'implication': 'Speculation'}])
    monkeypatch.setattr('scout.graph.model_json', lambda *args: fake)
    state = {'sources': SOURCES, 'mode': 'ollama'}
    state.update(analyze(state))
    with pytest.raises(ValueError):
        validate_evidence(state)
