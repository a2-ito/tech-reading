---
name: add-reading
description: 技術ブログ記事や論文の URL を引数に受け取り、その内容を読み取って `entries/YYYY-MM-DD-slug.md` にサマリ記事を1本生成するスキル。frontmatter（title / author / category / published / url）と「サマリ」「この記事から学べること（＋原文引用）」を含む md を作る。ユーザーが「/add-reading <URL>」と入力した場合、または「この記事をサマってリポジトリに追加して」「この論文を読んで entries に入れて」「記事のサマリを作って」のように URL を渡してこのリポジトリへエントリを追加する意図が読み取れる場合に発動する。
allowed-tools: WebFetch, Read, Write, Bash, ToolSearch
---

# add-reading

技術記事・論文の URL から、このリポジトリ形式のサマリ md を 1 本生成する。

## 入力

引数に URL を 1 つ受け取る。引数が無ければ「サマリ対象の URL を教えてください」と聞いて止まる。
複数 URL を渡された場合は、1 URL につき 1 ファイルを順に生成する。

## 手順

### 1. 本文を取得する

`WebFetch`（deferred の場合は先に `ToolSearch` で `select:WebFetch` を読み込む）で URL の内容を取得し、以下を抽出する。

- タイトル
- 著者（無ければ媒体名・組織名。それも無ければ `"Unknown"`）
- 出版日（`YYYY-MM-DD`。日付しか無い場合は分かる範囲で。取得不能なら `"Unknown"`）
- 本文の要旨と、引用に使える印象的な原文フレーズ

arXiv の abs ページなど取得しづらい場合は、同じ論文の HTML 版や abstract ページを試す。
取得に 2〜3 回失敗したら、無理に推測で書かず、ユーザーに状況を伝えて指示を仰ぐ。**本文を読めていない状態で内容を創作してはならない。**

### 2. カテゴリを決める

既存エントリのカテゴリに揃えるため、まず既存の値を確認する。

```bash
grep -h '^category:' entries/*.md 2>/dev/null | sort | uniq -c | sort -rn
```

近いものがあればそれを使い、無ければ新しいカテゴリを 1 語〜2 語で付ける（例: `LLM`, `Architecture`, `SRE`, `Security`, `Database`, `Engineering Management`）。

### 3. ファイル名を決める

`entries/<published>-<slug>.md`

- `<published>` は frontmatter の出版日。不明なら今日の日付を使い、frontmatter の `published` は `"Unknown"` のままにする。
- `<slug>` はタイトル由来の英小文字ケバブケース。日本語タイトルは意味を表す英単語に置き換える。3〜6 語程度に収める。
- 同名ファイルが既にある場合は上書きせず、ユーザーに「既にエントリがあります。更新しますか？」と確認する。

### 4. md を書く

`templates/entry.md` の構造に従う。

```markdown
---
title: "..."
author: "..."
category: "..."
published: "YYYY-MM-DD"
url: "..."
---

# タイトル

## サマリ

## この記事から学べること
```

- **サマリ**: 3〜6 行。課題 → 提案・主張 → 結果・結論 の流れで書く。
- **この記事から学べること**: 学びを 2〜4 個、`### 1. 見出し` 形式で立てる。各項目は「自分の言葉での説明」＋「原文からの引用（`>` ブロック）」の 2 点セットにする。
  - 引用は**原文をそのまま**写す。要約を引用として書かない。
  - 英語記事の引用は原文（英語）のまま載せ、必要なら説明側で日本語で補う。

文章は日本語。`~/.claude/skills/japanese-tech-writing` の規範が使える場合はそれに従い、一文一行で書く。

### 5. 報告する

生成したファイルパスと、タイトル・カテゴリを 1 行で報告する。コミットはユーザーの指示があるまで行わない。
