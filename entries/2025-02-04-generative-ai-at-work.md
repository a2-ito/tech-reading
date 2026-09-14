---
title: "Generative AI at Work"
author: "Erik Brynjolfsson, Danielle Li, Lindsey Raymond"
category: "AI Productivity"
published: "2025-02-04"
url: "https://doi.org/10.1093/qje/qjae044"
---

# Generative AI at Work

## サマリ

生成 AI が実際の職場でどれだけ生産性を上げるのかを、現場データで検証した論文。
Fortune 500 企業のカスタマーサポート 5,172 人を対象に、GPT-3 ベースの会話支援ツールが段階的に導入された過程を自然実験として扱っている。
結果は 1 時間あたりの解決件数が平均 15% 増加。
ただし効果は均一ではなく、経験の浅い低スキル層が 30% 増と大きく伸びる一方、最も熟練した層はほとんど伸びず、会話品質はわずかに低下した。
さらに AI 停止中でも生産性が維持されることから、単なる依存ではなく定着する学習が起きていること、顧客の態度が穏やかになり離職率が下がることも示された。

## この記事から学べること

### 1. 生成 AI の効果は「平均 15%」より「誰に効くか」が本質

全体平均だけ見ると 15% 増だが、この数字は実態をかなり隠している。
低スキル・低経験層は 30% 増、熟練層はほぼゼロか品質微減、と効果が正反対に分かれる。
過去の IT 投資が高スキル層を有利にしてきた (skill-biased technical change) のと逆向きの現象である点が、この論文の一番の驚きどころだ。
ツール導入の効果測定で平均値だけを見ると、判断を誤る。

> Access to AI assistance increases worker productivity, as measured by issues resolved per hour, by 15% on average, with substantial heterogeneity across workers.

> Less experienced and lower-skilled workers improve both the speed and quality of their output, while the most experienced and highest-skilled workers see small gains in speed and small declines in quality.

### 2. AI は経験曲線を前倒しする

熟練度の差が縮まる理由は、AI が熟練者の振る舞いを暗黙知ごと取り込んで配っているからだと解釈されている。
その効果は「勤続 2 ヶ月の AI 利用者が、勤続 6 ヶ月超の非利用者と同等」という形で現れる。
オンボーディング期間の短縮を定量的に示した記述として実務的な価値が高い。

> The AI tool also helps newer agents to move more quickly down the experience curve: treated agents with two months of tenure perform just as well as untreated agents with more than six months of tenure.

### 3. 効果は「依存」ではなく「学習」として定着する

AI 支援の効果が単なる寄りかかりなのか、本人の能力向上なのかは、導入判断でよく争点になる。
この論文は AI の障害停止という偶発イベントを使って切り分けている。
AI が使えない時間帯でも、導入前の水準を上回る生産性が観測された。
しかもその差は、AI への曝露が多く推奨をよく採用していた人ほど大きい。

> Using data on software outages—periods when the AI’s output is unexpectedly interrupted due to technical issues—we find that workers see productivity gains relative to their pre-AI baseline even when AI recommendations are unavailable.

### 4. 学習データの枯渇という長期リスク

短期の成果の裏で、著者らは不吉な循環を指摘している。
熟練者は品質がわずかに下がるにもかかわらず AI の推奨に従う割合を増やしていく。
熟練者の会話こそが AI の学習データの源泉なので、独自の解法が減れば将来のモデルは新しい問題に弱くなる。
AI 学習データへの貢献を評価する報酬設計が要る、という提言はここから出ている。

> In our data, top workers increase their adherence to AI recommendations, even though those recommendations marginally decrease the quality of their conversations. Yet with fewer original contributions from the most skilled workers, future iterations of the AI model may be less effective in solving new problems.

> our findings apply for a particular AI tool, used in a single firm, in a single occupation, and should not be generalized across all occupations and AI systems
