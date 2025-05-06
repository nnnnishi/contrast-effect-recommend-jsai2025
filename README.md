# The Application of Contrast Effects in Two-Sided Recommendation Systems --- JSAI2025

このリポジトリでは、「双方向推薦システムにおけるコントラスト効果の応用」の人工データを使用した検証のためのコードと実験設定が含まれています。

## 実験設定

### データ生成
- 一様分布に基づく候補データの生成：
  - ph1_score: [0, 1]
  - ph2_score: [0, 1]
  - ph3_score: [0, 1]

### ユーザー状態のモデル化
- 以下の要素に基づくユーザー状態スコアの計算：
  - ph1_count: フェーズ1の累積インタラクション数
  - steps_since_last_ph1: 最後のフェーズ1インタラクションからのステップ数
- 状態スコアの特性：
  - 範囲: [0, 2]
  - 初期値: 1（ph1_count = 0, steps_since_last_ph1 = 0の場合）
  - ph1_countによる対数的な増加
  - steps_since_last_ph1による指数的な減衰

### プラットフォームの動作
#### 静的シナリオ
- ユーザー状態に関係なくph1~3スコアは一定

#### 動的シナリオ
- ph1~3スコアはユーザー状態スコアに基づいて進化
- スコア更新: ph1~3_score * (user_state_score^(1/3))

### 評価指標
- 各フェーズ（ph1, ph2, ph3）の成功回数
- 成功確率の計算：
  - ph1: ph1_score * (user_state_score^(1/3))
  - ph2: ph2_score * (user_state_score^(1/3))（ph1が成功した場合のみ）
  - ph3: ph3_score * (user_state_score^(1/3))（ph2が成功した場合のみ）

## 実験パラメータ
- ユーザー数: 1000
- ユーザー状態: 一様分布
  - ph1_count ∈ [0, 50]
  - steps_since_last_ph1 ∈ [0, 50]
- アイテム数: 10（各ステップで新規生成）
- Top-kレコメンデーション: 1
- 実験ステップ数: 50
- 試行回数: 条件ごとに10セット
- 乱数シード: 42（再現性のため固定）

## 比較手法
### ベースライン
- レコメンデーション基準: ph1_score * ph2_score * ph3_score

### 提案手法
- レコメンデーション基準: ph1_score * ph2_score * ph3_score + λ * ph1_score * Δ
  - Δ: ユーザー状態スコアの変化量
  - λ ∈ {0.01, 0.1, 1}

## ユーザー状態の更新ルール
- ph1成功時：
  - ph1_countを1増加
  - last_ph1_stepを0にリセット
- ph1失敗時：
  - last_ph1_stepを1増加

## 終了条件
- ph3に成功したユーザーは除外（finished=True）
- ph3に失敗したユーザーは試行を継続

## ディレクトリ構成
```
.
├── src/
│   ├── data_processing/
│   ├── experiments/
│   ├── models/
│   ├── utils/
│   ├── config.py
│   ├── visualization/
│   └── README.md
├── data/
├── logs/
├── img/
├── results/
├── pyproject.toml
├── LICENSE
└── README.md
```

## 使用方法

### 1. 環境構築
Ryeを使用してPython環境を設定します：

```bash
# Ryeのインストール（まだの場合）
curl -sSf https://rye.astral.sh/get | bash

# プロジェクトの依存関係をインストール
rye sync

# 仮想環境をアクティベート
source .venv/bin/activate
```

### 2. データ生成
人工データを生成します：

```bash
# データ生成スクリプトを実行
python src/data_processing/create_data.py
```

### 3. 実験実行
実験を実行します：

```bash
# 実験スクリプトを実行
bash src/experiments/run_experiments.sh
```

このスクリプトは以下の実験を実行します：
- 静的シナリオ（decay=False）
- 動的シナリオ（decay=True）
- 各シナリオで異なるλ値（0.01, 0.1, 1）での実験

### 4. 結果の可視化
実験結果を可視化します：

```bash
# 可視化スクリプトを実行
bash src/visualization/run_visualize_results.sh
```

このスクリプトは以下の可視化を生成します：
- 各フェーズの成功確率の推移
- 累積ステップ数の比較
- 結果は`img/`ディレクトリに保存されます

### 5. 結果の確認
- 実験結果: `results/`ディレクトリ
- 可視化結果: `img/`ディレクトリ
- ログ: `logs/`ディレクトリ

