import numpy as np
import csv
from pathlib import Path
from config import USER_NUM, ITEM_NUM, RANDOM_SEED, EXPERIMENT_STEPS, TRIAL_NUM


def generate_user_initial_states(num_users):
    """
    各試行ごとのユーザーの初期状態を生成
    Returns:
        dict: {
            'ph1_counts': array of shape (num_users, num_items),
            'steps_since_last_ph1': array of shape (num_users, num_items)
        }
    """
    # 0-50の間で乱数を生成
    ph1_counts = np.random.randint(0, 51, num_users).tolist()
    steps_since_last_ph1 = np.random.randint(0, 51, num_users).tolist()

    return {"ph1_counts": ph1_counts, "steps_since_last_ph1": steps_since_last_ph1}


def generate_items(num_items, num_users, num_steps):
    """
    Userごとに各ステップで推薦するアイテムのスコアを生成
    """
    # ユーザー×ステップ数分のスコアを生成（小数点4桁まで）
    ph1_scores = np.round(
        np.random.rand(num_items, num_users * num_steps) * 0.1, 4
    ).tolist()
    ph2_scores = np.round(
        np.random.rand(num_items, num_users * num_steps) * 0.1, 4
    ).tolist()
    ph3_scores = np.round(
        np.random.rand(num_items, num_users * num_steps) * 0.1, 4
    ).tolist()

    return {
        "ph1_scores": ph1_scores,
        "ph2_scores": ph2_scores,
        "ph3_scores": ph3_scores,
    }


def main():
    # 出力ディレクトリの作成
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 乱数シードの設定
    np.random.seed(RANDOM_SEED)

    for trial in range(TRIAL_NUM):
        # 各試行で新しいユーザー初期状態を生成
        user_data = generate_user_initial_states(USER_NUM)
        # 各試行で新しいアイテムスコアを生成（ユーザー×ステップ数分）
        item_data = generate_items(ITEM_NUM, USER_NUM, EXPERIMENT_STEPS)
        # user_{trial_num}.csvとして保存
        user_data_path = data_dir / f"user_{trial}.csv"
        with open(user_data_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ph1_counts", "steps_since_last_ph1"])
            for ph1_count, step in zip(
                user_data["ph1_counts"], user_data["steps_since_last_ph1"]
            ):
                writer.writerow([ph1_count, step])

        # item_{trial_num}.csvとして保存
        item_data_path = data_dir / f"item_{trial}.csv"
        with open(item_data_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["user", "step", "item", "ph1_scores", "ph2_scores", "ph3_scores"]
            )

            # ユーザー×ステップ数分の行を書き込む
            for u in range(USER_NUM):
                for s in range(EXPERIMENT_STEPS):
                    for item_idx in range(ITEM_NUM):
                        writer.writerow(
                            [
                                u,
                                s,
                                item_idx,
                                item_data["ph1_scores"][item_idx][u * s],
                                item_data["ph2_scores"][item_idx][u * s],
                                item_data["ph3_scores"][item_idx][u * s],
                            ]
                        )


if __name__ == "__main__":
    main()
