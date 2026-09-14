#!/usr/bin/env python3
"""entries/ 配下のエントリがリポジトリの書式に沿っているか検証する。

違反があれば標準出力に一覧を出し、終了コード 1 で終わる。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ENTRIES_DIR = Path(__file__).resolve().parent.parent / "entries"

REQUIRED_KEYS = ("title", "author", "category", "published", "url")
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}(?:-\d{2})?)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
PUBLISHED_RE = re.compile(r"^(?:\d{4}-\d{2}(?:-\d{2})?|Unknown)$")
CHECKED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SUMMARY_HEADING = "## サマリ"
LEARNINGS_HEADING = "## この記事から学べること"
RECEPTION_HEADING = "## 一般の評価"


@dataclass(frozen=True)
class Violation:
    path: str
    message: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """先頭の YAML frontmatter を素朴に解析し、(フィールド, 本文行) を返す。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, lines

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        fields[key.strip()] = value.strip().strip('"').strip("'").strip()

    return fields, lines[end + 1 :]


def section(body: list[str], heading: str) -> list[str] | None:
    """指定の見出しに属する行を返す。見出しが無ければ None。"""
    try:
        start = body.index(heading)
    except ValueError:
        return None

    out: list[str] = []
    for line in body[start + 1 :]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def check_frontmatter(name: str, fields: dict[str, str]) -> list[Violation]:
    violations: list[Violation] = []

    if not fields:
        return [Violation(name, "frontmatter (--- で囲まれたブロック) が先頭にありません")]

    for key in REQUIRED_KEYS:
        if not fields.get(key):
            violations.append(Violation(name, f"frontmatter の `{key}` が無い、または空です"))

    published = fields.get("published", "")
    if published and not PUBLISHED_RE.match(published):
        violations.append(
            Violation(name, f"`published` は YYYY-MM-DD / YYYY-MM / Unknown のいずれか: {published!r}")
        )

    url = fields.get("url", "")
    if url and not url.startswith(("http://", "https://")):
        violations.append(Violation(name, f"`url` は http(s) で始まる必要があります: {url!r}"))

    checked = fields.get("reception_checked", "")
    if not checked:
        violations.append(
            Violation(name, "`reception_checked` が無い、または空です (scripts/fetch_reception.py で取得できます)")
        )
    elif not CHECKED_RE.match(checked):
        violations.append(
            Violation(name, f"`reception_checked` は YYYY-MM-DD 形式にしてください: {checked!r}")
        )

    return violations


def check_filename(name: str, fields: dict[str, str]) -> list[Violation]:
    match = FILENAME_RE.match(name)
    if not match:
        return [
            Violation(name, "ファイル名は `YYYY-MM-DD-slug.md` 形式 (slug は英小文字ケバブケース) にしてください")
        ]

    published = fields.get("published", "")
    if published and published != "Unknown" and match.group(1) != published:
        return [
            Violation(name, f"ファイル名の日付 {match.group(1)} が frontmatter の published {published} と一致しません")
        ]

    return []


def check_body(name: str, body: list[str]) -> list[Violation]:
    violations: list[Violation] = []

    summary = section(body, SUMMARY_HEADING)
    if summary is None:
        violations.append(Violation(name, f"`{SUMMARY_HEADING}` セクションがありません"))
    elif not any(line.strip() for line in summary):
        violations.append(Violation(name, f"`{SUMMARY_HEADING}` の中身が空です"))

    reception = section(body, RECEPTION_HEADING)
    if reception is None:
        violations.append(Violation(name, f"`{RECEPTION_HEADING}` セクションがありません"))
    else:
        lines = [l for l in reception if l.strip()]
        if not lines:
            violations.append(Violation(name, f"`{RECEPTION_HEADING}` の中身が空です"))
        elif not any(l.startswith("*") and "時点" in l for l in lines):
            violations.append(
                Violation(name, f"`{RECEPTION_HEADING}` に取得日 (`*YYYY-MM-DD 時点*`) がありません")
            )
        elif not any(l.startswith("-") for l in lines):
            violations.append(
                Violation(name, f"`{RECEPTION_HEADING}` に指標の箇条書きがありません（取得できない場合も「確認できず」と明記する）")
            )

    learnings = section(body, LEARNINGS_HEADING)
    if learnings is None:
        violations.append(Violation(name, f"`{LEARNINGS_HEADING}` セクションがありません"))
        return violations

    subsections: list[tuple[str, list[str]]] = []
    for line in learnings:
        if line.startswith("### "):
            subsections.append((line[4:].strip(), []))
        elif subsections:
            subsections[-1][1].append(line)

    if not subsections:
        violations.append(
            Violation(name, f"`{LEARNINGS_HEADING}` の下に `### ` の学び見出しが 1 つもありません")
        )

    for heading, lines in subsections:
        if not any(line.startswith(">") for line in lines):
            violations.append(Violation(name, f"学び `{heading}` に引用 (`>` ブロック) がありません"))
        if not any(line.strip() and not line.startswith(">") for line in lines):
            violations.append(Violation(name, f"学び `{heading}` に引用以外の説明文がありません"))

    return violations


def main() -> int:
    if not ENTRIES_DIR.is_dir():
        print(f"entries ディレクトリが見つかりません: {ENTRIES_DIR}")
        return 1

    paths = sorted(ENTRIES_DIR.glob("*.md"))
    violations: list[Violation] = []
    seen_urls: dict[str, str] = {}

    for path in paths:
        name = path.name
        fields, body = parse_frontmatter(path.read_text(encoding="utf-8"))

        violations.extend(check_frontmatter(name, fields))
        violations.extend(check_filename(name, fields))
        violations.extend(check_body(name, body))

        url = fields.get("url", "")
        if url:
            if url in seen_urls:
                violations.append(Violation(name, f"`url` が {seen_urls[url]} と重複しています: {url}"))
            else:
                seen_urls[url] = name

    if violations:
        print(f"検証 NG: {len(paths)} 件中 {len({v.path for v in violations})} 件のエントリに問題があります\n")
        for v in violations:
            print(f"  entries/{v.path}: {v.message}")
        print("\n書式は README.md と templates/entry.md を参照してください。")
        return 1

    print(f"検証 OK: {len(paths)} 件のエントリはすべて書式を満たしています")
    return 0


if __name__ == "__main__":
    sys.exit(main())
