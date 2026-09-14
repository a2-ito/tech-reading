---
name: add-reading
description: 技術ブログ記事や論文の URL を引数に受け取り、その内容を読み取って `entries/YYYY-MM-DD-slug.md` にサマリ記事を1本生成し、Pull Request の作成まで行うスキル。frontmatter（title / author / category / published / url / reception_checked）と「サマリ」「一般の評価」「この記事から学べること（＋原文引用）」を含む md を作り、被引用数や Hacker News の反応といった外部評価を取得し、引用を原文と照合したうえで 1 記事 1 PR で提出する。ユーザーが「/add-reading <URL>」と入力した場合、または「この記事をサマってリポジトリに追加して」「この論文を読んで entries に入れて」「記事のサマリを作って」のように URL を渡してこのリポジトリへエントリを追加する意図が読み取れる場合に発動する。
allowed-tools: WebFetch, Read, Write, Bash, ToolSearch, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__tabs_close_mcp
---

# add-reading

技術記事・論文の URL から、このリポジトリ形式のサマリ md を 1 本生成し、Pull Request にして提出する。

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

WebFetch のサマリは引用が省略・要約されることがあるため、**引用を使うなら原文テキストを自分で取得する**。
取得できないときは次の順に試す。

1. `curl` に User-Agent などブラウザ相当のヘッダを付ける（これで 403 が解けることが多い）
2. PDF なら `curl` で落として `pdftotext -layout` にかける
3. それでも 403 なら `mcp__claude-in-chrome__navigate` と `get_page_text` でブラウザ経由で読む（開いたタブは `tabs_close_mcp` で閉じる）

ここまでやって取得できなければ、無理に推測で書かず、ユーザーに状況を伝えて指示を仰ぐ。**本文を読めていない状態で内容を創作してはならない。**

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
reception_checked: "YYYY-MM-DD"
---

# タイトル

## サマリ

## 一般の評価

## この記事から学べること
```

- **サマリ**: 3〜6 行。課題 → 提案・主張 → 結果・結論 の流れで書く。
- **この記事から学べること**: 学びを 2〜4 個、`### 1. 見出し` 形式で立てる。各項目は「自分の言葉での説明」＋「原文からの引用（`>` ブロック）」の 2 点セットにする。
  - 引用は**原文をそのまま**写す。要約を引用として書かない。
  - 英語記事の引用は原文（英語）のまま載せ、必要なら説明側で日本語で補う。

文章は日本語。`~/.claude/skills/japanese-tech-writing` の規範が使える場合はそれに従い、一文一行で書く。

### 5. 外部評価を取得する

記事が広く読まれたものか、一個人の意見に留まるものかを区別できるようにする。

```bash
python3 scripts/fetch_reception.py <URL>
```

出力された frontmatter 行を `url:` の直後に、本文セクションを `## サマリ` と `## この記事から学べること` の間に貼る。

守ること。

- **取得日 (`reception_checked`) を必ず添える。** 指標は時間とともに変わるため、日付のない数値は誤解を生む
- **取得できなかった指標は空欄にせず「確認できず」と明記する。** Hacker News に投稿が無いことは評価が低いことを意味しない。単にその媒体が Hacker News 向きでないだけの場合が多く、空欄のまま放置すると読み手が誤読する
- 数値の解釈をサマリ側に書かない。評価はセクションの数値として提示し、読み手の判断に委ねる

論文で URL に DOI が含まれない場合は、DOI 形式の URL を `url` に使うと被引用数が取得できる。

### 6. 引用を原文と照合する

**引用は必ず原文と突き合わせて検証する。** 記憶や要約から書き起こしてはならない。

取得した原文テキストを一時ファイルに保存し、md 内の `> ` 行がすべて原文に含まれることをスクリプトで確認する。
空白の畳み込みは行ってよい。
PDF は行末ハイフンと透かし行の除去が必要になる。

照合スクリプトは、原文を空白正規化した文字列に対して各引用が部分文字列として含まれるかを調べるだけでよい。

一致しない引用は、正しい原文に直すか削除する。
サイトの規約などで大量の転記を避ける必要がある場合は、引用を 1 文単位に絞り、**照合が目視に留まったことをユーザーへの報告と PR 本文に明記する**。

### 7. リポジトリの検証を通す

`python3 scripts/validate_entries.py` を実行する。
エラーが出たら直してから次に進む。
これは CI で走るものと同じ検証である。

### 8. コミットして PR を作成する

**1 記事 1 PR とする。** 複数記事を 1 つの PR にまとめない。

手順は `git fetch origin` でベースブランチを最新化してから `git switch -c add-reading/<slug> origin/main` でブランチを切り、該当エントリだけを `git add` してコミットし、push して `gh pr create` する。

守ること。

- **ベースブランチを最新化してからブランチを切る**（`git fetch` を先に実行する）
- コミットメッセージは Conventional Commits 形式、本文は日本語（`docs: 「タイトル」のサマリを追加`）
- ラベルは `feature` / `ai-assisted` / `ai-generated` を付与し、PR 本文末尾に明記する
- **トークンや署名付きの一時 URL を frontmatter に書かない。** このリポジトリは public であり、自動マージで即座に公開される。`url` には DOI や記事の正典 URL を記載し、差し替えたことを PR 本文に書く
- PR 本文には、学べることの一覧、検証結果、原文取得で特筆すべきことがあれば記載する

PR を出すと `validate` が走り、通れば自動的にマージされる。
マージを確認したら、ローカルとリモートの作業ブランチを削除して片付ける。

### 9. 報告する

生成したファイルパス、タイトル、カテゴリ、外部評価の主な数値、PR の URL を報告する。
引用の照合結果と、原文取得で通常と異なる手順を踏んだ場合はその旨も添える。
