"""
Wire-level auth tests: prove that JiraClient + the jira library together emit
the correct ``Authorization`` header for each auth method.

Unlike test_client.py (which mocks ``jira.JIRA`` and only checks how we call it),
these exercise the real jira client and intercept the outgoing HTTP request at
the transport layer (``HTTPAdapter.send``). No network or live Jira is required,
but the assertion is on the actual header requests would put on the wire —
Bearer for PAT, Basic for basic auth.
"""

import base64

import jira.client
import requests
import requests.adapters

from cac_jira.core.client import JiraClient


def _capture_authorization(monkeypatch, username, token, auth_method):
    """Build a JiraClient and return the Authorization header of the first
    HTTP request the jira client actually sends."""
    captured = {}

    def fake_send(self, request, **kwargs):
        captured.setdefault("authorization", request.headers.get("Authorization"))
        resp = requests.models.Response()
        resp.status_code = 200
        # Superset payload that satisfies both serverInfo and myself parsing.
        resp._content = (
            b'{"version": "9.4.0", "versionNumbers": [9, 4, 0], '
            b'"deploymentType": "Server", "accountId": "123", '
            b'"name": "tester", "key": "tester"}'
        )
        resp.headers["Content-Type"] = "application/json"
        resp.encoding = "utf-8"
        resp.url = request.url
        resp.request = request
        return resp

    # conftest globally mocks ``jira.JIRA``; restore the real client (still
    # available at jira.client.JIRA) so an actual request is built and sent.
    monkeypatch.setattr("jira.JIRA", jira.client.JIRA)

    # Patch the base transport adapter so every request (including any made
    # inside jira.JIRA.__init__) is intercepted, regardless of jira's custom
    # session/retry wrapper.
    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", fake_send)

    JiraClient("jira.example.com", username, token, auth_method=auth_method)
    return captured["authorization"]


def test_pat_sends_bearer_authorization(monkeypatch):
    auth = _capture_authorization(
        monkeypatch, None, "PAT-secret-123", auth_method="pat"
    )
    assert auth == "Bearer PAT-secret-123"


def test_basic_sends_basic_authorization(monkeypatch):
    auth = _capture_authorization(
        monkeypatch, "user@example.com", "api-token-123", auth_method="basic"
    )
    assert auth is not None
    assert auth.startswith("Basic ")
    decoded = base64.b64decode(auth.split(" ", 1)[1]).decode()
    assert decoded == "user@example.com:api-token-123"
