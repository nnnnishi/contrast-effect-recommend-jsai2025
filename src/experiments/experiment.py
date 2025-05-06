#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import time
import random
import json
import numpy as np
from datetime import datetime
import sys
import csv

from utils.utils import (
    calculate_user_state_score,
    get_user_state_score_delta,
)

from config import (
    USER_NUM,
    ITEM_NUM,
    TOP_K,
    EXPERIMENT_STEPS,
    TRIAL_NUM,
    RANDOM_SEED,
    RESULTS_DIR,
    LOGS_DIR,
    ModelConfig,
)

from models.models import User, Item

# このファイルのディレクトリの親（src）をパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def setup_logger():
    """ロギング設定を行います"""
    log_dir = LOGS_DIR
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"experiment_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def load_data(trial: int) -> tuple[list[User], list[Item]]:
    """
    実験用のユーザーデータとアイテムデータを読み込む

    Args:
        trial: 実験試行回数
    Returns:
        tuple[list[User], list[Item]]: ユーザーリストとアイテムデータのリスト
    """
    # ユーザーデータの読み込み
    user_file = os.path.join("data", f"user_{trial}.csv")
    users = []

    with open(user_file, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= USER_NUM:  # ユーザー数に達したら終了
                break
            user = User(
                id=i,
                ph1_count=int(row["ph1_counts"]),
                last_ph1_step=int(row["steps_since_last_ph1"]),
                finished=False,
            )
            users.append(user)

    # アイテムデータの読み込み
    item_file = os.path.join("data", f"item_{trial}.csv")
    items = []

    with open(item_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            user_id = int(row["user"])
            step = int(row["step"])
            item_id = int(row["item"])

            if item_id < ITEM_NUM:
                item = Item(
                    user=user_id,
                    step=step,
                    item=item_id,
                    ph1_score=float(row["ph1_scores"]),
                    ph2_score=float(row["ph2_scores"]),
                    ph3_score=float(row["ph3_scores"]),
                )
                items.append(item)

    return users, items


def run_experiment(lambda_val: float, decay_flag: bool):
    """指定されたλ値で実験を実行します"""
    logger = logging.getLogger(__name__)
    logger.info(f"実験を開始します: λ = {lambda_val}, 減衰フラグ = {decay_flag}")

    start_time = time.time()

    all_results = {"lambda": lambda_val, "trials": []}

    for trial in range(TRIAL_NUM):
        logger.info(f"試行 {trial + 1}/{TRIAL_NUM} を開始")

        # 試行ごとに固定の乱数シードを設定
        trial_seed = RANDOM_SEED + trial
        random.seed(trial_seed)
        np.random.seed(trial_seed)

        # ユーザーとアイテムデータを読み込む
        users, items = load_data(trial)

        # 各フェーズの成功回数を記録
        trial_results = {"ph1": 0, "ph2": 0, "ph3": 0}

        # 最初にitemsをユーザーとステップでグループ化した辞書を作成
        items_dict = {}
        for item in items:
            key = (item.user, item.step)
            if key not in items_dict:
                items_dict[key] = []
            items_dict[key].append(item)

        # 実験ステップのループ
        for step in range(EXPERIMENT_STEPS):
            # 各ユーザーの処理
            step_score = {"ph1": 0, "ph2": 0, "ph3": 0}
            for user in users:
                if user.finished:
                    continue

                # λ=0の場合はbaselineスコア、それ以外はproposedスコアを使用
                if lambda_val == 0:
                    # 辞書から直接ユーザーとステップに関連するアイテムを取得
                    user_items = items_dict.get((user.id, step), [])
                    sorted_items = sorted(
                        user_items,
                        key=ModelConfig.baseline_score,
                        reverse=True,
                    )
                else:
                    delta = get_user_state_score_delta(
                        user.ph1_count, user.last_ph1_step
                    )
                    # 辞書から直接ユーザーとステップに関連するアイテムを取得
                    user_items = items_dict.get((user.id, step), [])
                    sorted_items = sorted(
                        user_items,
                        key=lambda x: ModelConfig.proposed_score(x, delta, lambda_val),
                        reverse=True,
                    )

                top_k_items = sorted_items[:TOP_K]
                for item in top_k_items:
                    user_status = calculate_user_state_score(
                        user.ph1_count, user.last_ph1_step
                    )
                    # decay_flagによって確率の計算方法を切り替え
                    if decay_flag:
                        ph1_prob = item.ph1_score * (
                            user_status ** ModelConfig.SCORE_ADJUSTMENT["ph1"]
                        )
                        ph2_prob = item.ph2_score * (
                            user_status ** ModelConfig.SCORE_ADJUSTMENT["ph2"]
                        )
                        ph3_prob = item.ph3_score * (
                            user_status ** ModelConfig.SCORE_ADJUSTMENT["ph3"]
                        )
                    else:
                        ph1_prob = item.ph1_score
                        ph2_prob = item.ph2_score
                        ph3_prob = item.ph3_score

                    if random.random() < ph1_prob:
                        step_score["ph1"] += 1
                        user.ph1_count += 1
                        user.last_ph1_step = 0

                        if random.random() < ph2_prob:
                            step_score["ph2"] += 1

                            if random.random() < ph3_prob:
                                step_score["ph3"] += 1
                                user.finished = True
                    else:
                        user.last_ph1_step += 1

            # 結果を累積
            for phase in ["ph1", "ph2", "ph3"]:
                trial_results[phase] += step_score[phase]

        # 試行結果を記録
        all_results["trials"].append(trial_results)

    # 平均値を計算
    average_results = {
        "ph1": float(np.mean([trial["ph1"] for trial in all_results["trials"]])),
        "ph2": float(np.mean([trial["ph2"] for trial in all_results["trials"]])),
        "ph3": float(np.mean([trial["ph3"] for trial in all_results["trials"]])),
    }

    all_results["average"] = average_results
    all_results["execution_time"] = time.time() - start_time

    logger.info(f"実験が完了しました: λ = {lambda_val}, 平均結果 = {average_results}")
    return all_results


def save_results(results, output_dir=RESULTS_DIR):
    """実験結果を保存します"""
    logger = logging.getLogger(__name__)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lambda_val = results["lambda"]

    # 結果をJSON形式で保存
    results_file = os.path.join(output_dir, f"lambda_{lambda_val}_{timestamp}.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"結果を保存しました: {results_file}")


def parse_arguments():
    """コマンドライン引数をパースします"""
    parser = argparse.ArgumentParser(description="実験実行スクリプト")
    parser.add_argument(
        "--lambda_value",
        type=float,
        default=0.1,
        help="将来マッチング重視パラメータλ (0.0はbaseline相当)",
    )
    parser.add_argument(
        "--no_decay_flag",
        action="store_false",
        dest="decay_flag",
        help="減衰なしにしたい場合はこのフラグを指定",
    )
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    print(args)
    logger = setup_logger()

    logger.info("プログラムを開始します")

    try:
        results = run_experiment(args.lambda_value, args.decay_flag)
        if args.decay_flag:
            output_dir = "results/decay_true"
        else:
            output_dir = "results/decay_false"
        save_results(results, output_dir)
        logger.info("プログラムが正常に終了しました")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
