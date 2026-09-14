#!/usr/bin/env python3
"""記事・論文の外部評価（被引用数と推移、Hacker News の反応、Wikipedia からの参照、GitHub star）を取得する。

使い方:
    python3 scripts/fetch_reception.py <URL>

frontmatter に貼る行と、本文に貼る「## 一般の評価」セクションを出力する。
取得できなかった指標は空欄にせず「確認できず」と明示する。数値には常に取得日を添える。

ドメイン人気度（Tranco 等）や検索順位は意図的に採用していない。理由は README を参照。
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
USER_AGENT = "tech-reading-reception/1.0 (https://github.com/a2-ito/tech-reading)"
TIMEOUT = 30


class FetchError(RuntimeError):
    """外部 API の取得に失敗したことを示す。"""


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} from {url}") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise FetchError(f"{type(e).__name__}: {e} ({url})") from e


@dataclass
class Reception:
    """1 記事分の外部評価。取得できなかった指標は None のままにする。"""

    citations: int | None = None
    fwci: float | None = None
    percentile: str | None = None
    hn_submissions: int = 0
    hn_points: int | None = None
    hn_comments: int | None = None
    hn_url: str | None = None
    citation_trend: list[tuple[int, int]] = field(default_factory=list)
    wikipedia_refs: dict[str, int] = field(default_factory=dict)
    github_stars: int | None = None
    github_repo: str | None = None
    notes: list[str] = field(default_factory=list)


def extract_doi(url: str) -> str | None:
    m = re.search(r"doi\.org/(10\.[^\s?#]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", url)
    return m.group(1) if m else None


def fetch_openalex(doi: str, out: Reception) -> None:
    data = get_json(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}")
    out.citations = data.get("cited_by_count")
    fwci = data.get("fwci")
    out.fwci = round(fwci, 1) if isinstance(fwci, (int, float)) else None

    counts = data.get("counts_by_year") or []
    out.citation_trend = sorted(
        (c["year"], c["cited_by_count"]) for c in counts if c.get("cited_by_count")
    )[-4:]

    pct = data.get("citation_normalized_percentile") or {}
    if pct.get("is_in_top_1_percent"):
        out.percentile = "top 1%"
    elif pct.get("is_in_top_10_percent"):
        out.percentile = "top 10%"
    elif isinstance(pct.get("value"), (int, float)):
        out.percentile = f"top {round((1 - pct['value']) * 100)}%"


def fetch_hn(url: str, out: Reception) -> None:
    """URL で Hacker News の投稿を検索する。スキームと www の有無を吸収する。"""
    bare = re.sub(r"^https?://", "", url).rstrip("/")
    query = re.sub(r"^www\.", "", bare)
    params = urllib.parse.urlencode(
        {"query": query, "restrictSearchableAttributes": "url", "hitsPerPage": "50"}
    )
    hits = get_json(f"https://hn.algolia.com/api/v1/search?{params}").get("hits", [])
    if not hits:
        return

    out.hn_submissions = len(hits)
    best = max(hits, key=lambda h: h.get("points") or 0)
    out.hn_points = best.get("points")
    out.hn_comments = best.get("num_comments")
    out.hn_url = f"https://news.ycombinator.com/item?id={best.get('objectID')}"


def fetch_wikipedia(url: str, out: Reception) -> None:
    """Wikipedia の本文から、この URL が出典として参照されている記事数を数える。

    ドメイン全体ではなくパスまで含めて検索するため、記事単位の指標になる。
    """
    query = re.sub(r"^https?://", "", url).rstrip("/")
    for lang in ("en", "ja"):
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "list": "exturlusage",
                "euquery": query,
                "eulimit": "100",
                "eunamespace": "0",
                "format": "json",
            }
        )
        data = get_json(f"https://{lang}.wikipedia.org/w/api.php?{params}")
        hits = (data.get("query") or {}).get("exturlusage") or []
        if hits:
            out.wikipedia_refs[lang] = len(hits)


def fetch_github(url: str, out: Reception) -> None:
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+)/([^/?#]+)", url)
    if not m:
        return
    repo = f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
    data = get_json(f"https://api.github.com/repos/{repo}")
    out.github_stars = data.get("stargazers_count")
    out.github_repo = repo


def collect(url: str) -> Reception:
    out = Reception()

    doi = extract_doi(url)
    if doi:
        try:
            fetch_openalex(doi, out)
        except FetchError as e:
            out.notes.append(f"OpenAlex の取得に失敗: {e}")
    else:
        out.notes.append("DOI が URL から取れないため被引用数は未取得")

    for fn, label in (
        (fetch_hn, "Hacker News"),
        (fetch_wikipedia, "Wikipedia"),
        (fetch_github, "GitHub"),
    ):
        try:
            fn(url, out)
        except FetchError as e:
            out.notes.append(f"{label} の取得に失敗: {e}")

    return out


def render(url: str, r: Reception, today: str) -> str:
    fm = [f'reception_checked: "{today}"']
    if r.citations is not None:
        fm.append(f"citations: {r.citations}")
    if r.percentile:
        fm.append(f'citation_percentile: "{r.percentile}"')
    if r.hn_points is not None:
        fm.append(f"hn_points: {r.hn_points}")
        fm.append(f"hn_comments: {r.hn_comments}")
    if r.wikipedia_refs:
        fm.append(f"wikipedia_refs: {sum(r.wikipedia_refs.values())}")
    if r.github_stars is not None:
        fm.append(f"github_stars: {r.github_stars}")

    body = ["## 一般の評価", "", f"*{today} 時点*", ""]
    if r.citations is not None:
        extra = []
        if r.percentile:
            extra.append(f"分野内 {r.percentile}")
        if r.fwci is not None:
            extra.append(f"FWCI {r.fwci}")
        suffix = f"（OpenAlex、{'、'.join(extra)}）" if extra else "（OpenAlex）"
        body.append(f"- 被引用数 {r.citations} 件{suffix}")
        if r.citation_trend:
            trend = " → ".join(f"{y}年 {c}" for y, c in r.citation_trend)
            body.append(f"- 被引用の推移: {trend}")
    else:
        body.append("- 学術的な被引用数は該当なし（論文ではないため）")

    if r.hn_points is not None:
        plural = f"（投稿 {r.hn_submissions} 件のうち最大のもの）" if r.hn_submissions > 1 else ""
        body.append(
            f"- Hacker News: [{r.hn_points}pt / {r.hn_comments} コメント]({r.hn_url}){plural}"
        )
    else:
        body.append("- Hacker News への投稿は確認できず")

    if r.wikipedia_refs:
        langs = "、".join(f"{lang}: {n} ページ" for lang, n in sorted(r.wikipedia_refs.items()))
        body.append(f"- Wikipedia から出典として参照: {langs}")
    else:
        body.append("- Wikipedia からの参照は確認できず")

    if r.github_stars is not None:
        body.append(f"- GitHub: {r.github_stars} stars（{r.github_repo}）")

    out = ["=== frontmatter に追記 ===", "", *fm, "", "=== 本文に追記 ===", "", *body]
    if r.notes:
        out += ["", "=== 備考 ===", "", *[f"- {n}" for n in r.notes]]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2

    url = argv[1]
    today = datetime.now(JST).date().isoformat()
    print(render(url, collect(url), today))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
