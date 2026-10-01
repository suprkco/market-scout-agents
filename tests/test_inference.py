import httpx
import pytest
from pydantic import ValidationError

from scout.evaluate import evidence_scores, run_case
from scout.inference import capture_calls, model_json
from scout.models import Critique


def mock_response(monkeypatch, content='{"concerns":[]}', finish='stop'):
    monkeypatch.setenv('SCOUT_BACKEND', 'llamacpp')

    def post(url, **kwargs):
        assert kwargs['json']['response_format']['schema']['additionalProperties'] is False
        assert kwargs['json']['cache_prompt'] is False
        return httpx.Response(200, request=httpx.Request('POST', url), json={
            'choices': [{'message': {'content': content}, 'finish_reason': finish}],
            'usage': {'prompt_tokens': 12, 'completion_tokens': 4}})

    monkeypatch.setattr('scout.inference.httpx.post', post)


def test_capture_preserves_usage_and_output_without_changing_result(monkeypatch):
    mock_response(monkeypatch)
    with capture_calls() as calls:
        assert model_json(Critique, 'Review', []).concerns == []
    assert calls[0]['usage']['prompt_tokens'] == 12
    assert calls[0]['valid_schema'] is True
    assert calls[0]['wall_seconds'] >= 0


@pytest.mark.parametrize('content,finish,error', [
    ('{"concerns":[]}', 'length', ValueError),
    ('{"concerns":[],"approved":true}', 'stop', ValidationError),
    ('not json', 'stop', ValidationError),
])
def test_invalid_and_truncated_outputs_remain_failures(monkeypatch, content, finish, error):
    mock_response(monkeypatch, content, finish)
    with capture_calls() as calls, pytest.raises(error):
        model_json(Critique, 'Review', [])
    assert calls[0]['raw_output'] == content
    assert calls[0]['valid_schema'] is False


def test_quote_coverage_does_not_reward_fabrication_or_duplicates():
    sources = [{'id': 'a', 'text': 'Actual supplied source passage.'},
               {'id': 'b', 'text': 'A different supplied source.'}]
    findings = [{'source_id': 'a', 'quote': 'Actual supplied source passage.'}] * 2
    findings += [{'source_id': 'a', 'quote': 'Invented'},
                 {'source_id': 'unknown', 'quote': 'Actual supplied source passage.'}]
    assert evidence_scores(findings, sources) == {
        'findings': 4, 'exact_quote_matches': 2, 'covered_sources': 1, 'supplied_sources': 2}


def test_failed_call_is_retained_in_evaluation_and_cannot_publish(monkeypatch):
    mock_response(monkeypatch, 'not json')
    sources = [{'id': 'a', 'title': 'Public announcement', 'url': 'https://example.org',
                'text': 'A sufficiently long public source passage.'}]
    row = run_case({'id': 'case', 'source_ids': ['a']}, sources)
    assert row['error']['type'] == 'ValidationError'
    assert row['calls'][0]['raw_output'] == 'not json'
    assert not row['awaiting_human_review']
    assert not row['report_emitted']
