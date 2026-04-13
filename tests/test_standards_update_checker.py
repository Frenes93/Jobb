import os
import sys

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.standards_update_checker import (  # noqa: E402
    StandardTarget,
    StandardsUpdateChecker,
    format_text_report,
)


def test_check_targets_detects_standard_name():
    html = "<html><title>ISO Search</title><body>Latest release for ISO 15156 part 1.</body></html>"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html)

    transport = httpx.MockTransport(handler)
    target = StandardTarget(code="ISO 15156", source="ISO", search_url="https://example.test/iso")

    with httpx.Client(transport=transport) as client:
        checker = StandardsUpdateChecker()
        result = checker._check_one(client, target)

    assert result.found is True
    assert result.page_title == "ISO Search"
    assert "ISO 15156" in (result.matched_snippet or "")


def test_format_text_report_includes_status():
    html = "<html><title>NORSOK</title><body>No relevant data here.</body></html>"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html)

    transport = httpx.MockTransport(handler)
    target = StandardTarget(code="NORSOK M-650", source="NORSOK", search_url="https://example.test/norsok")

    with httpx.Client(transport=transport) as client:
        checker = StandardsUpdateChecker()
        result = checker._check_one(client, target)

    report = format_text_report([result])
    assert "IKKE FUNNET" in report
    assert "HTTP 200" in report
