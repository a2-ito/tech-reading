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
