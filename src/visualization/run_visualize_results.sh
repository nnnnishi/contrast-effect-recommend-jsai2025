#!/bin/bash

ROOT_DIR=$(dirname `readlink -f $0`)

# 実験ディレクトリのパスを設定
python $ROOT_DIR/visualize_results.py