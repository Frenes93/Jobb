from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class StandardTarget:
    """A standard and where to look for updates."""

    code: str
    source: str
    search_url: str
    note: str = ""


@dataclass(frozen=True)
class StandardUpdateResult:
    code: str
    source: str
    search_url: str
    checked_at: str
    status_code: int
    found: bool
    page_title: str | None
    matched_snippet: str | None
    note: str = ""


DEFAULT_TARGETS: list[StandardTarget] = [
    StandardTarget(
        code="ISO 15156",
        source="ISO Online Browsing Platform",
        search_url="https://www.iso.org/search.html?q=ISO%2015156",
        note="Material standards for H2S service.",
    ),
    StandardTarget(
        code="NORSOK M-650",
        source="Standard Norge NORSOK catalogue",
        search_url="https://online.standard.no/nb/standarder/norsok/",
        note="Qualification of manufacturers.",
    ),
]


class StandardsUpdateChecker:
    """Check configured sources for visible mentions of standards."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def check_targets(self, targets: Iterable[StandardTarget]) -> list[StandardUpdateResult]:
        return [self._check_one(target) for target in targets]

    def _check_one(self, target: StandardTarget) -> StandardUpdateResult:
        checked_at = datetime.now(timezone.utc).isoformat()

        try:
            status_code, html = _fetch_url(target.search_url, timeout=self.timeout)
            found = target.code.lower() in html.lower()
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            page_title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else None
            snippet = _extract_match_snippet(html, target.code) if found else None

            return StandardUpdateResult(
                code=target.code,
                source=target.source,
                search_url=target.search_url,
                checked_at=checked_at,
                status_code=status_code,
                found=found,
                page_title=page_title,
                matched_snippet=snippet,
                note=target.note,
            )
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            return StandardUpdateResult(
                code=target.code,
                source=target.source,
                search_url=target.search_url,
                checked_at=checked_at,
                status_code=0,
                found=False,
                page_title=None,
                matched_snippet=f"Feil ved henting: {exc}",
                note=target.note,
            )


def _fetch_url(url: str, timeout: float) -> tuple[int, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "Jobb-standards-checker/1.0 (+https://example.local)",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        status_code = getattr(response, "status", None) or response.getcode()
        body = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        html = body.decode(charset, errors="replace")
    return int(status_code), html


def _extract_match_snippet(html: str, query: str, radius: int = 70) -> str | None:
    match = re.search(re.escape(query), html, flags=re.IGNORECASE)
    if not match:
        return None

    start = max(match.start() - radius, 0)
    end = min(match.end() + radius, len(html))
    raw = html[start:end]
    cleaned = re.sub(r"<[^>]+>", " ", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def load_targets_from_file(path: str) -> list[StandardTarget]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    targets: list[StandardTarget] = []
    for item in data:
        targets.append(
            StandardTarget(
                code=item["code"],
                source=item["source"],
                search_url=item["search_url"],
                note=item.get("note", ""),
            )
        )
    return targets


def format_text_report(results: list[StandardUpdateResult]) -> str:
    lines = []
    for result in results:
        status = "FUNNET" if result.found else "IKKE FUNNET"
        lines.append(
            f"- {result.code} ({result.source}) -> {status}, HTTP {result.status_code}, sjekket {result.checked_at}"
        )
        if result.page_title:
            lines.append(f"  Tittel: {result.page_title}")
        if result.matched_snippet:
            lines.append(f"  Utdrag: {result.matched_snippet}")
        if result.note:
            lines.append(f"  Merknad: {result.note}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Søk etter oppdateringer/treff på ISO- og NORSOK-standarder. "
            "Legg inn egen liste via JSON-fil ved behov."
        )
    )
    parser.add_argument(
        "--targets-file",
        help="JSON-fil med liste av standarder og søke-URLer. Hvis utelatt brukes standardliste i programmet.",
    )
    parser.add_argument("--json", action="store_true", help="Skriv resultat som JSON i stedet for tekst.")
    args = parser.parse_args()

    targets = load_targets_from_file(args.targets_file) if args.targets_file else DEFAULT_TARGETS
    checker = StandardsUpdateChecker()
    results = checker.check_targets(targets)

    if args.json:
        print(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2))
    else:
        print(format_text_report(results))


if __name__ == "__main__":
    main()
