# tech-readins

技術ブログ記事・論文を読んだサマリを 1 記事 1 ファイルで蓄積するリポジトリ。

## 構成

```
entries/     読んだ記事・論文のサマリ（1記事 = 1 md）
templates/   エントリのテンプレート
.claude/     スキル定義
```

## エントリの書式

各 md は frontmatter と本文からなる。

| フィールド | 内容 |
| --- | --- |
| `title` | 記事・論文のタイトル |
| `author` | 著者名（複数は `,` 区切り） |
| `category` | カテゴリ（LLM / Architecture / SRE / Security など） |
| `published` | 出版日 (`YYYY-MM-DD`) |
| `url` | 元記事の URL |

本文は以下の 2 セクション。

- **サマリ** — 何の課題に、何を提案し、どうだったか
- **この記事から学べること** — 学びごとに見出しを立て、説明＋原文からの引用を添える

## ファイル名

`entries/YYYY-MM-DD-slug.md`（`YYYY-MM-DD` は出版日、`slug` はタイトル由来の英小文字ケバブケース）

## エントリの追加

Claude Code で URL を渡してスキルを呼ぶ。

```
/add-reading https://example.com/article
```

URL の内容を取得し、上記書式のエントリを `entries/` に生成する。
# tech-reading

## CI

PR を作成すると `validate` ワークフローが自動実行され、`entries/` 配下の全エントリが書式を満たしているか検証する。

```bash
python3 scripts/validate_entries.py   # ローカルでも同じ検証を実行できる
```

検証する項目は以下。

- frontmatter に `title` / `author` / `category` / `published` / `url` がすべて存在し、空でない
- `published` が `YYYY-MM-DD` / `YYYY-MM` / `Unknown` のいずれか
- ファイル名が `YYYY-MM-DD-slug.md` 形式で、日付部分が `published` と一致する
- `url` が http(s) で始まり、他のエントリと重複しない
- `## サマリ` と `## この記事から学べること` の両方が存在し、サマリが空でない
- 学びの `###` 見出しが 1 つ以上あり、各見出しが引用 (`>`) と説明文の両方を持つ

### PR の自動処理について

**CI は PR を自動でクローズしない。**
`validate` の結果はチェックとして表示するだけで、マージするか閉じるかは人間が判断する。

fork 由来の PR と外部作者の PR も同様に、ワークフローが自動で操作することはない。

`validate` は次の構成で、権限昇格の経路を持たない。

| | `validate` |
| --- | --- |
| トリガ | `pull_request` / `push` (main) |
| 権限 | `contents: read` のみ |
| secrets | 渡らない |
| 書き込み | 一切行わない |

fork からの PR でも `GITHUB_TOKEN` は read-only で secrets も渡らないため、PR のコードを checkout して検証しても安全である。
書き込み権限を持つワークフローはこのリポジトリに存在しない。
