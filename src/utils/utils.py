import numpy as np
from typing import List
import os
import sys

from models.models import User, Item

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


class UserStateScoreParams:
    """ユーザ状態スコアの計算に使用するパラメータ

    Attributes:
        MAX_PH1_COUNT (int): ph1カウントの上限値。これを超えると増加が止まる
        MAX_STEPS (int): 経過ステップ数の上限値。これを超えると減少が止まる
        BASE_SCORE (float): 初期スコア。(ph1_count, steps_since_last_ph1) = (0, 0)のときの値
        MAX_SCORE_MULTIPLIER (float): 最大スコア倍率。ph1_count = MAX_PH1_COUNTのときのスコア
        DECAY_RATE (float): 経過ステップごとの減衰率。
                           MAX_STEPSステップ経過時にスコアが0.1となるように設定
                           0.1 = DECAY_RATE^MAX_STEPS より、
                           DECAY_RATE = 0.1^(1/MAX_STEPS)
    """

    MAX_PH1_COUNT = 100  # ph1カウントの上限
    MAX_STEPS = 100  # 経過ステップ数の上限
    BASE_SCORE = 1.0  # 初期スコア
    MAX_SCORE_MULTIPLIER = 2.0  # 最大スコア倍率
    DECAY_RATE = 0.1 ** (1 / MAX_STEPS)  # 経過ステップごとの減衰率


def calculate_user_state_score(ph1_count: int, steps_since_last_ph1: int) -> float:
    """
    ユーザの状態スコアを計算する

    Args:
        ph1_count: ph1の累計数（最大100）
        steps_since_last_ph1: 最後のph1実行からの経過ステップ数（最大100）

    Returns:
        user_state_score: 0から2の範囲のスコア、(ph1_count, steps_since_last_ph1) = (0, 0)のときの初期値は1
    """
    # 上限を制限
    ph1_count = min(ph1_count, UserStateScoreParams.MAX_PH1_COUNT)
    steps_since_last_ph1 = min(steps_since_last_ph1, UserStateScoreParams.MAX_STEPS)

    # 累計数の影響（対数関数的な増加）
    if ph1_count == 0:
        score = UserStateScoreParams.BASE_SCORE
    else:
        # 1 + log1p(ph1_count) / log1p(MAX_PH1_COUNT)
        score = UserStateScoreParams.BASE_SCORE + (
            np.log1p(ph1_count) / np.log1p(UserStateScoreParams.MAX_PH1_COUNT)
        )

    # 経過ステップ数の影響（指数関数的な減衰）
    # DECAY_RATEは経過ステップ数がMAX_STEPSのときに0.1になるように設定
    score = score * (UserStateScoreParams.DECAY_RATE**steps_since_last_ph1)

    return score


def generate_items(n_items: int, random_seed: int = 42) -> List[Item]:
    """
    アイテムを生成する

    Args:
        n_items: 生成するアイテム数
        random_seed: 乱数シード

    Returns:
        items: 生成されたアイテムのリスト
    """
    np.random.seed(random_seed)

    items = []
    for i in range(n_items):
        item = Item(
            id=i,
            ph1_score=np.random.uniform(0, 0.2),
            ph2_score=np.random.uniform(0, 0.2),
            ph3_score=np.random.uniform(0, 0.2),
        )
        items.append(item)

    return items


def generate_users(n_users: int) -> List[User]:
    """
    ユーザを生成する

    Args:
        n_users: 生成するユーザ数

    Returns:
        users: 生成されたユーザのリスト
    """
    return [User(id=i) for i in range(n_users)]


def get_user_state_score_delta(current_ph1_count: int, current_steps: int) -> float:
    """
    ph1実行後のuser_state_scoreの変化量を計算する

    Args:
        current_ph1_count: 現在のph1累計数
        current_steps: 現在の経過ステップ数
    Returns:
        delta: スコアの変化量
    """
    current_score = calculate_user_state_score(current_ph1_count, current_steps)
    next_score = calculate_user_state_score(current_ph1_count + 1, 0)
    return next_score - current_score


def calculate_step_ratios(history: dict, steps: list = [10, 20, 30, 40, 50]) -> dict:
    """
    特定のステップでのbaselineに対する比を計算する

    Args:
        history: ステップごとのスコア履歴
        steps: 比率を計算するステップのリスト

    Returns:
        step_ratios: ステップごとの比率
    """
    step_ratios = {step: {"ph1": 0.0, "ph2": 0.0, "ph3": 0.0} for step in steps}

    for step in steps:
        if step >= len(history["baseline"]["ph1"]):
            continue

        # 各ステップまでの累積値を計算
        baseline_cumsum = {
            phase: sum(history["baseline"][phase][:step])
            for phase in ["ph1", "ph2", "ph3"]
        }
        proposed_cumsum = {
            phase: sum(history["proposed"][phase][:step])
            for phase in ["ph1", "ph2", "ph3"]
        }

        # 比率の計算
        for phase in ["ph1", "ph2", "ph3"]:
            if baseline_cumsum[phase] > 0:
                step_ratios[step][phase] = (
                    proposed_cumsum[phase] / baseline_cumsum[phase]
                )
            else:
                step_ratios[step][phase] = 0.0

    return step_ratios


def calculate_metrics(
    baseline_score: dict, proposed_score: dict, history: dict = None
) -> dict:
    """
    baselineとproposedの比較指標を計算する

    Args:
        baseline_score: baselineの各フェーズのスコア
        proposed_score: proposedの各フェーズのスコア
        history: ステップごとのスコア履歴 (オプション)

    Returns:
        metrics: 各種評価指標
    """
    metrics = {
        "raw_counts": {
            "baseline": baseline_score,
            "proposed": proposed_score,
        },
        "ratios": {},  # baselineに対する比
        "step_ratios": {},  # 特定のステップでの比率
    }

    # baselineに対する比の計算
    for phase in ["ph1", "ph2", "ph3"]:
        if baseline_score[phase] > 0:
            metrics["ratios"][phase] = proposed_score[phase] / baseline_score[phase]
        else:
            metrics["ratios"][phase] = 0

    # 特定のステップでの比率を計算
    if history:
        metrics["step_ratios"] = calculate_step_ratios(history)

    return metrics
