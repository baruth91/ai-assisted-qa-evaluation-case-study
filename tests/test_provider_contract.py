import json

import pytest

from qa_ai.provider import client, generate, model_metadata


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class FakeSession:
    def __init__(self):
        self.payload = None

    def post(self, url, *, json, timeout):
        self.payload = json
        return FakeResponse({"done": True, "done_reason": "stop", "message": {"content": "{}"}})


def test_ground_truth_labels_are_not_sent_to_the_model(cases, schema):
    session = FakeSession()
    config = {"model": "test-fixture", "options": {"seed": 42}}
    generate(session, "http://127.0.0.1:11434", config, "A versioned prompt", cases[0], schema)
    user_message = json.loads(session.payload["messages"][1]["content"])
    assert set(user_message) == {"requirements", "acceptance_criteria"}
    assert "evaluation" not in user_message
    assert session.payload["format"] == schema
    assert session.payload["stream"] is False


@pytest.mark.parametrize("url", ["https://example.com", "http://example.com", "ftp://localhost"])
def test_teaching_adapter_refuses_nonlocal_targets(url):
    with pytest.raises(ValueError, match="loopback"):
        client(url)


def test_model_digest_drift_fails_before_generation():
    class MetadataSession:
        def get(self, url, *, timeout):
            if url.endswith("version"):
                return FakeResponse({"version": "test-runtime"})
            return FakeResponse({"models": [{"name": "test-model", "digest": "different"}]})

    with pytest.raises(ValueError, match="digest changed"):
        model_metadata(
            MetadataSession(),
            "http://127.0.0.1:11434",
            {"model": "test-model", "expected_digest": "original"},
        )
