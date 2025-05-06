# 実験実行スクリプト

このディレクトリには、推薦システムの実験を実行するためのスクリプトが含まれています。

## 使用方法

### 基本的な実行方法

```bash
python experiment.py --lambda_value 0.1 --output results/decay_true
```

### 引数

- `--lambda_value`: 将来マッチング重視パラメータλ（0.0はbaseline相当）
  - デフォルト値: 0.1
- `--output`: 結果出力ディレクトリ
  - デフォルト値: "results/decay_true"

### 実験の概要

このスクリプトは以下の処理を行います：

1. 指定されたλ値で実験を実行
2. 各試行で以下のデータを処理：
   - ユーザーデータ（`data/user_{trial}.csv`）
   - アイテムデータ（`data/item_{trial}.csv`）
3. 実験結果をJSON形式で保存
   - ファイル名: `lambda_{lambda_value}_{timestamp}.json`

### 出力ファイル

実験結果は以下の情報を含みます：
- 使用したλ値
- 各試行の結果（ph1, ph2, ph3の成功回数）
- 全試行の平均結果
- 実行時間

### ログ

実験の実行ログは`logs`ディレクトリに保存されます：
- ファイル名: `experiment_{timestamp}.log`
