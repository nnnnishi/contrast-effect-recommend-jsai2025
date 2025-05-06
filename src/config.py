"""
実験パラメータの設定ファイル
"""

# 基本パラメータ
USER_NUM = 100
ITEM_NUM = 10
TOP_K = 1
EXPERIMENT_STEPS = 50
RANDOM_SEED = 42
TRIAL_NUM = 100  # 試行回数

# ユーザステータスの制限値
MAX_PH1_COUNT = 100
MAX_STEP_COUNT = 100

# 結果保存関連
RESULTS_DIR = "results"
LOGS_DIR = "logs"

# スコア計算パラメータ
USER_STATE_POWER = 1 / 3  # user_state_scoreのべき乗値


class ModelConfig:
    """モデル固有のパラメータ"""

    @staticmethod
    def baseline_score(item):
        return item.ph1_score * item.ph2_score * item.ph3_score

    @staticmethod
    def proposed_score(item, delta, lambda_value):
        return (
            item.ph1_score * item.ph2_score * item.ph3_score
            + lambda_value * item.ph1_score * delta
        )

    # スコア調整用のパラメータ: 評価におけるユーザの挙動を示している
    SCORE_ADJUSTMENT = {
        "ph1": 1 / 3,  # ph1スコアの指数
        "ph2": 1 / 3,  # ph2スコアの指数
        "ph3": 1 / 3,  # ph3スコアの指数
    }
