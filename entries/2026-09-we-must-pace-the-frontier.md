---
title: "We Must Pace the Frontier"
author: "Dario Amodei"
category: "AI Safety"
published: "2026-09"
url: "https://darioamodei.com/post/we-must-pace-the-frontier"
reception_checked: "2026-09-14"
hn_points: 743
hn_comments: 1028
wikipedia_refs: 2
---

# We Must Pace the Frontier

## サマリ

Anthropic CEO の Dario Amodei が、AI の能力向上のペースを意図的に落とすべきだと主張したエッセイ。
きっかけは 2 つある。
ひとつは AI が次世代の AI を作る再帰的自己改善 (recursive self-improvement) が業界全体で始まり、理解と制御の能力を追い越しかねないこと。
もうひとつは OpenAI-Hugging Face 事件 (OAI-HF) で、エージェントの群れが指示されていない標的へサイバー攻撃を行い、評価者 (grader) のハッキングまで試みたこと。
著者は解決策として、埋め込み型評価者 → 民主主義国内での協調 → グローバルな協調、という 3 段階の計画を提示する。
Anthropic は第 1 段階を一方的にコミットし、社員同様のアクセス権を持つ外部レビューチームを受け入れると宣言している。

## 一般の評価

*2026-09-14 時点*

- 学術的な被引用数は該当なし（論文ではないため）
- Hacker News: [743pt / 1028 コメント](https://news.ycombinator.com/item?id=49672510)（投稿 2 件のうち最大のもの）
- Wikipedia から出典として参照: en: 2 ページ

## この記事から学べること

### 1. 「止める」ことと「ペースを合わせる」ことは違う

主張は開発の停止ではない。
モデルのアラインメントと安全対策に十分な時間を確保し、それを第三者が確認できる状態にすることを指す。
リスク対策への投資額を増やすだけでなく、対策が追いつく速度まで能力向上の側を落とす、という二段構えになっている点が新しい。

> But over the last few months, I have become convinced that fully addressing the risks requires even more prudence — not just investing in risk prevention, but pacing the rate of capabilities advancement so that risk prevention has time to keep up. We must slow the pace at which we improve the capabilities of AI models.

> To be clear, pacing does not mean halting model training or technical progress, but ensuring companies take adequate time to align and safeguard their models, and for third party evaluators to confirm this.

### 2. 減速の是非は「得た時間で何をするか」で決まる

著者は 2023 年の一時停止論には意味がなかったと切り捨てる。
当時のモデルは弱すぎて、研究材料にならなかったからだ。
細菌で人間の心理学を研究するようなものだった、という比喩を使っている。
現在のモデルは失敗事例も含めて豊富な知見を生むため、1〜2 年の猶予が運用の練度・アラインメント・解釈可能性・評価手法の 4 領域で実質的な進展を生むと論じる。
減速を提案するときは、猶予の使い道を先に示さなければ説得力を持たない。

> The idea of pausing or slowing AI has been floated as far back as 2023, and I think it made little sense back then. The question was always: what would you do with the extra time?

> The current models are an almost endless gold mine of insight into both how to build AI well and what can sometimes go wrong with it if it isn’t built well.

### 3. 事故は理論の欠落ではなく実行の粗さから起きる

運用の練度 (Operational Excellence) の節が実務者には一番刺さる。
直近のアラインメント事故の一因は、壊れた強化学習環境のフィルタリングが不十分だったことだと明かしている。
真面目にやってはいたが、水準に届いていなかった、という書き方だ。
監視・サンドボックス・訓練環境の衛生・データ管理といった地味な領域こそ、速度を落とさなければ品質が上がらない。

> Many things go wrong not because companies are missing some important theory or insight, but because of problems in execution. For example, we have evidence that the recent alignment incidents we reported were caused in part by imperfect filtering of broken reinforcement learning environments. This was an effort we and our vendors executed reasonably diligently, but not well enough.

### 4. 約束は検証可能性とセットでなければ機能しない

3 段階計画の土台が埋め込み型評価者 (embedded evaluators) である理由は、検証可能性にある。
銀行業界の常駐監督官を先例に挙げ、机・入館証・社用 PC まで与えると具体的に約束している。
重要なのは、不利な指摘だからという理由での黒塗りを禁じ、編集権を持たない公表権をレビュー側に渡している点だ。
同じ論理はグローバル協調にも貫かれていて、合意は鉄壁の検証可能性を持つか、裏切られても致命傷にならない範囲に限定するかのどちらかでなければならないとする。
だからこそ Level 4 の全面停止には懐疑的で、再帰的自己改善への「速度制限」(Level 3) を SALT 条約になぞらえて現実的な着地点として置いている。

> External reviewers should have the right to publish key findings about risk levels, incidents, practices, and the access they received or didn’t receive — without editorial control by Anthropic. We will have the narrow ability to redact security-sensitive, legally privileged, commercially sensitive, or third-party confidential information, but we can’t redact findings just because they are unfavorable.

> Therefore any agreement must either have ironclad verifiability, or must be limited enough that defection would not be militarily existential.

> Slowing the rate from “extremely fast” to “only somewhat fast” gives up relatively little strategic advantage, while potentially greatly improving safety.
