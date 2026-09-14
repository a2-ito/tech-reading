---
title: "The AI-Native SDLC playbook"
author: "Louis Claxton (Anthropic)"
category: "Software Engineering"
published: "2026-08-21"
url: "https://claude.com/blog/the-ai-native-sdlc-playbook"
reception_checked: "2026-09-14"
hn_points: 7
hn_comments: 1
---

# The AI-Native SDLC playbook

## サマリ

コーディングがボトルネックでなくなった前提で、ソフトウェア開発ライフサイクル全体をどう組み直すかを段階ごとに示した実践ガイド。
出発点の問題意識は、AI がコードを書く速度は劇的に上がったのに、その周囲にある承認・レビュー・引き継ぎの仕組みが旧来のままだという非対称にある。
提案は、Plan / Design / Build / Test / Deploy / Maintain の 6 段階を直線ではなくループとして捉え直し、各段階を「バージョン管理にコミットされた成果物」で接続するというもの。
`intent.md` → `spec.md` → `plan.md` → 差分とテスト → レビュー所見つき PR → インシデント記録、と繋がり、このコミットの連鎖がそのまま監査証跡になる。
統制は会議ではなく hooks・サンドボックス・ブランチ保護といったコードで強制し、人間の判断は各ゲートに集約される。

## 一般の評価

*2026-09-14 時点*

- 学術的な被引用数は該当なし（論文ではないため）
- Hacker News: [7pt / 1 コメント](https://news.ycombinator.com/item?id=49451263)（投稿 5 件のうち最大のもの）

## この記事から学べること

### 1. ボトルネックは消えるのではなく、左右に移動する

build が速くなっても全体が速くなるとは限らない。
計画・レビュー・デプロイという人間速度の工程が残り、そこに滞留が移るだけだからだ。
さらに厄介なのは、統制そのものが現実に追随できなくなる点である。
差分の大半をエージェントが書くようになると、全行を人が読むという前提が崩れる。
セキュリティレビューを例に、レビュー待ち行列が伸びるか、レビュー不足のまま出荷されるかの二択になると指摘している。

> Organizations have started using AI to write code at a speed unthinkable one year ago, yet the processes around the code haven't changed at the same pace.

> The controls stop matching reality and become intractable. Reviewing each line by hand made sense when a person had written it, but it can't keep up once agents write most of the diff.

### 2. 段階を繋ぐのはチケットではなくコミットされた成果物

この playbook の設計上の核心はここだと思う。
各段階は成果物をバージョン管理に書き込んで終わり、次の段階はそれを読んで始まる。
前半で `.md` を使うのは、プロダクトオーナーとエージェントの双方が同じファイルを読んで動けるからだと説明されている。
そして受け渡しの記録がそのまま「誰が何を頼み、エージェントが何を出し、誰が承認したか」の監査証跡になる。
ドキュメントを別に作るのではなく、工程の副産物として証跡が積み上がる構造になっている。

> Each stage ends by writing one to version control (including intent.md, spec.md, plan.md, the diff and its tests, the PR with its review findings, and the incident record) and the next stage begins by reading it.

> The chain of commits is also the audit trail: who asked for what, what the agent produced, and who approved it.

### 3. ガバナンスは会議ではなくコードとして走らせる

例外処理が週次・月次の会議に流れる限り、統制コストは開発速度に比例して増えていく。
そこで承認ゲートを hooks として実装し、権限・サンドボックス・ブランチ保護で境界を引く。
方針は明快で、エージェントは本番ゲートの手前までは動けるが、そのゲートは越えられない。
修正案を出したエージェント自身にそれを承認する経路が無い、という設計も同じ思想の現れである。

> The governing principle is that the agent may act up to the production gate and cannot pass it.

> The agent that proposed the fix has no route to approve it.

> Humans remain accountable for every decision that requires judgment.

### 4. 自律ループの安全弁は「検知を決定論に保つ」こと

最終段階では、人間が起動しなくてもループが回る状態を目指す。
本番の異常を検知したら診断し、所見を `intent.md` として書き戻して最初の段階に戻す。
ここで巧いのは、検知側にモデルを使わないと明言している点だ。
検知は統計的な管理限界を見るだけの決定論的スクリプトに留め、逸脱の度合いに応じてエージェントの裁量を段階化する。
1σ は記録のみ、2σ は読み取り専用の診断、3σ で初めて PR 作成や事前承認済み runbook の実行を許す、という具合である。

> Detection stays deterministic. Claude is invoked once a band is breached, and the tier sets what it may do.

> At 1σ the script only logs, at 2σ it invokes Claude read-only to diagnose, and at 3σ Claude may act, though only by opening a PR into the review gate or triggering a pre-approved runbook.

> The loop keeps running. Human judgement stays above it.
