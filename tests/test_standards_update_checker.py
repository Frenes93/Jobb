import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "app" / "services" / "standards_update_checker.py"
SPEC = importlib.util.spec_from_file_location("standards_update_checker", MODULE_PATH)
checker_mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = checker_mod
SPEC.loader.exec_module(checker_mod)

StandardTarget = checker_mod.StandardTarget
StandardsUpdateChecker = checker_mod.StandardsUpdateChecker
format_text_report = checker_mod.format_text_report


def test_check_targets_detects_standard_name(monkeypatch):
    html = "<html><title>ISO Search</title><body>Latest release for ISO 15156 part 1.</body></html>"

    def fake_fetch_url(url: str, timeout: float):
        return 200, html

    monkeypatch.setattr(checker_mod, "_fetch_url", fake_fetch_url)

    target = StandardTarget(code="ISO 15156", source="ISO", search_url="https://example.test/iso")
    checker = StandardsUpdateChecker()
    result = checker._check_one(target)

    assert result.found is True
    assert result.page_title == "ISO Search"
    assert "ISO 15156" in (result.matched_snippet or "")


def test_format_text_report_includes_status(monkeypatch):
    html = "<html><title>NORSOK</title><body>No relevant data here.</body></html>"

    def fake_fetch_url(url: str, timeout: float):
        return 200, html

    monkeypatch.setattr(checker_mod, "_fetch_url", fake_fetch_url)

    target = StandardTarget(code="NORSOK M-650", source="NORSOK", search_url="https://example.test/norsok")
    checker = StandardsUpdateChecker()
    result = checker._check_one(target)

    report = format_text_report([result])
    assert "IKKE FUNNET" in report
    assert "HTTP 200" in report
