# データ生成スクリプト

このディレクトリには、実験用のデータを生成するスクリプトが含まれています。

## create_data.py

このスクリプトは、実験に必要な以下のデータを生成します：
- ユーザーの初期状態（ph1_counts, steps_since_last_ph1）
- アイテムのスコア（ph1_scores, ph2_scores, ph3_scores）

### 生成されるデータ

- `data/user_{trial}.csv`: 各試行のユーザー初期状態
  - カラム: ph1_counts, steps_since_last_ph1
- `data/item_{trial}.csv`: 各試行のアイテムスコア
  - カラム: user, step, item, ph1_scores, ph2_scores, ph3_scores

### 使用方法

1. 必要なパッケージをインストール:
```bash
pip install numpy
```

2. スクリプトを実行:
```bash
python create_data.py
```

### 設定

`config.py`で以下のパラメータを設定できます：
- `USER_NUM`: ユーザー数
- `ITEM_NUM`: アイテム数
- `RANDOM_SEED`: 乱数シード
- `EXPERIMENT_STEPS`: 実験ステップ数
- `TRIAL_NUM`: 試行回数

### 注意事項

- 実行前に`data`ディレクトリが存在することを確認してください
- 生成されるデータは乱数に基づいているため、同じ`RANDOM_SEED`を使用すると同じデータが生成されます
