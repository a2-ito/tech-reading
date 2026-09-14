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
| `reception_checked` | 外部評価を取得した日 (`YYYY-MM-DD`) |
| `citations` ほか | 取得できた指標のみ記載（`citations` / `citation_percentile` / `hn_points` / `hn_comments` / `github_stars`） |

本文は以下の 3 セクション。

- **サマリ** — 何の課題に、何を提案し、どうだったか
- **一般の評価** — 被引用数や Hacker News の反応など、第三者による受け止め
- **この記事から学べること** — 学びごとに見出しを立て、説明＋原文からの引用を添える

## 一般の評価

記事が広く読まれたものか、一個人の意見に留まるものかを区別するために、外部の評価指標を記録する。

```bash
python3 scripts/fetch_reception.py <URL>
```

取得元はいずれも無料・APIキー不要。

| 指標 | 取得元 | 対象 |
| --- | --- | --- |
| 被引用数 / FWCI / パーセンタイル / 年次推移 | OpenAlex | URL から DOI が取れる論文 |
| 投稿数 / スコア / コメント数 | Hacker News (Algolia) | すべて |
| 出典として参照している記事数 | Wikipedia (en / ja) | すべて |
| star 数 | GitHub API | URL が GitHub リポジトリのとき |

**数値は必ず取得日 (`reception_checked`) とセットで記録する。** 指標は時間とともに変わるため、日付のない数値は誤解を生む。

**取得できなかった指標は空欄にせず「確認できず」と明記する。** Hacker News に投稿が無いことは、その記事の評価が低いことを意味しない。単にその媒体が Hacker News 向きでないだけの場合が多く、空欄のまま放置すると読み手が誤読する。

### 採用しない指標

**ドメイン人気度と検索順位は採用しない。** これらは記事の中身ではなくドメインの強さをほぼそのまま反映するため、このリポジトリの目的に対して逆向きに働く。

実測した例を挙げる。

| 記事 | Tranco ドメイン順位 | Hacker News |
| --- | --- | --- |
| Forbes の記事 | 213 位 | 投稿なし |
| BCG の記事 | 4,337 位 | 投稿なし |
| Amodei のエッセイ | 100 万位以内に入らず | 743pt / 1026 コメント |

大手媒体は何を載せても上位に出る一方、個人ドメインは反響の大きさに関わらず下位になる。
「広く読まれた記事か、一個人の意見か」を区別したいのに、ドメイン評価で並べると順序が反転する。

その他、以下は技術的な理由で対象外としている。

- Google の検索順位 — 順位を返す API が公開されていない。Custom Search JSON API は API キーが必要なうえ実際の検索順位とは別物で、結果のスクレイピングは利用規約に反する
- PageRank — 2016 年に一般公開が終了している
- 被リンク数 — 無料で取得できる API が無い（Ahrefs、Moz などは有料）
- Altmetric — DOI 向けの API が 403 を返すため利用できない

### 指標の読み方

指標が無いことは、評価が低いことを意味しない。

- Hacker News に投稿が無い記事は多い。媒体や読者層が Hacker News 向きでないだけの場合が大半である
- Wikipedia は更新が遅いため、新しい記事はほぼ参照 0 になる
- 被引用数は累計だけを見ると「昔の名作」と「今まさに読まれている研究」を区別できない。年次推移を併記しているのはこのため

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

### 自動マージ

内部 PR は `validate` が通ると自動的にマージされる。

```
PR 作成
  ├─ validate が走る
  └─ auto-merge が GitHub ネイティブの auto-merge を有効化する
        ↓
     validate 通過を GitHub が待ってマージ
```

`auto-merge` ワークフロー自体はマージを実行しない。
有効化するだけで、実際のマージは必須ステータスチェック `validate-entries` の通過後に GitHub が行う。

自動マージを止めたい PR には `keep-open` ラベルを付ける。
draft の PR も対象外になる。

### 外部 PR の扱い

自動マージの対象は**このリポジトリ内のブランチから出された、書き込み権限を持つ作者の PR のみ**。
fork 由来の PR と外部作者の PR は自動マージされず、人間が判断する。

ガードは 3 重になっている。

1. fork からの PR では `GITHUB_TOKEN` が read-only になるため、有効化 API を呼ぶこと自体ができない（GitHub の仕組みによる保証）
2. ジョブの `if` で `head.repo.full_name == github.repository` を確認し、fork を明示的に除外する
3. `author_association` が `OWNER` / `MEMBER` / `COLLABORATOR` のいずれかであることを確認する

また、どちらのワークフローも **PR のコードを checkout しない / 実行しない**。
`validate` は PR のコードを実行するが `contents: read` のみで書き込み権限を持たず、`auto-merge` は書き込み権限を持つが PR のコードに触れない。
権限とコード実行が同じジョブに同居しない構成にしてある。

### リポジトリ設定

自動マージには以下の設定が必要。

- リポジトリ設定の `Allow auto-merge` が有効
- `main` の ruleset で `validate-entries` を必須ステータスチェックに指定

ruleset が無いと PR がブロックされず、ネイティブ auto-merge は成立しない。
リポジトリ管理者は bypass actor に設定してあるため、`main` への直接 push は従来どおり可能。
