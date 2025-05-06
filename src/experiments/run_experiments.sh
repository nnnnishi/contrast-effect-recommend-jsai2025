#!/bin/bash

ROOT_DIR=$(dirname `readlink -f $0`)

# 実験パラメータの設定
lambda_values=(0 0.001 0.01 0.1 1)
decay_flags=("" "--no_decay_flag")

# 結果ディレクトリの作成
mkdir -p $ROOT_DIR/../../results/decay_true
mkdir -p $ROOT_DIR/../../results/decay_false

# 結果ディレクトリの中のjsonファイルを削除
rm -f $ROOT_DIR/../../results/decay_true/*.json
rm -f $ROOT_DIR/../../results/decay_false/*.json

# 各パラメータの組み合わせで実験を実行
for lambda in "${lambda_values[@]}"; do
    for decay in "${decay_flags[@]}"; do
        echo "Running experiment with lambda=$lambda, decay=$decay"
        python $ROOT_DIR/experiment.py --lambda_value $lambda $decay
    done
done

echo "All experiments completed!" 
