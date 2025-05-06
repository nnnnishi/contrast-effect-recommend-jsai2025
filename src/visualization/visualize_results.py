import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib_fontja


def summarize_and_plot(result_dir, plot_filename_prefix):
    # ディレクトリ内のすべてのJSONファイルを取得
    json_files = list(result_dir.glob("*.json"))
    # 結果を格納するデータフレームを初期化
    results = []

    # 各ファイルを処理
    for file in json_files:
        # ファイルからデータを読み込む
        with open(file, "r") as f:
            data = json.load(f)
        lambda_val = file.name.split("_")[1]
        # 平均スコアを記録
        if "average" in data:
            for score_metric in ["ph1", "ph2", "ph3"]:
                if score_metric in data["average"]:
                    results.append(
                        {
                            "lambda": lambda_val,
                            "metric": f"{score_metric}_score",
                            "value": data["average"][score_metric],
                        }
                    )

    # λ=0.0のデータを基準として比率を計算
    df = pd.DataFrame(results)
    # λ=0.0のデータを抽出
    lambda_0_df = df[df["lambda"] == "0.0"]

    # 各メトリクスのλ=0.0の値を取得
    baseline_values = {}
    for _, row in lambda_0_df.iterrows():
        metric = row["metric"]
        baseline_values[metric] = row["value"]

    # 比率を計算
    for i, row in df.iterrows():
        metric = row["metric"]
        if metric in baseline_values:
            baseline = baseline_values[metric]
            df.at[i, "baseline"] = baseline
            df.at[i, "ratio"] = (
                row["value"] / baseline if baseline != 0 else float("inf")
            )

    # 結果を表示
    print(f"{result_dir} λ=0.0との比率:")
    print(df.pivot(index="lambda", columns="metric", values="ratio"))

    # 詳細な結果を表示
    print(f"\n{result_dir} 詳細な結果:")
    print(
        df.pivot(
            index=["lambda", "metric"],
            columns=[],
            values=["value", "baseline", "ratio"],
        )
    )

    # 結果をCSVファイルに保存
    output_file = result_dir / f"{plot_filename_prefix}_summary_ratios.csv"
    df.to_csv(output_file, index=False)
    print(f"\n結果を{output_file}に保存しました。")

    # グラフの作成
    plt.figure(figsize=(8, 8))

    # フォントサイズを大きく設定
    plt.rcParams["font.size"] = 14
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 18
    plt.rcParams["xtick.labelsize"] = 28
    plt.rcParams["ytick.labelsize"] = 28
    plt.rcParams["legend.fontsize"] = 14

    # λ値をソート
    lambda_values = sorted(df["lambda"].unique(), key=lambda x: float(x))

    # 全メトリクスを取得
    all_metrics = df["metric"].unique()

    # メトリクスごとの色を定義
    color_map = {"ph1_score": "red", "ph2_score": "green", "ph3_score": "blue"}

    for metric in all_metrics:
        metric_df = df[df["metric"] == metric]
        if not metric_df.empty:
            sorted_df = pd.DataFrame(
                {
                    "lambda": lambda_values,
                    "ratio": [
                        metric_df[metric_df["lambda"] == lv]["ratio"].values[0]
                        if lv in metric_df["lambda"].values
                        else np.nan
                        for lv in lambda_values
                    ],
                }
            )
            plt.plot(
                sorted_df["lambda"],
                sorted_df["ratio"],
                marker="o",
                label=metric,
                color=color_map.get(metric),
            )

    plt.axhline(y=1.0, color="black", linestyle="--", alpha=0.5)
    plt.xlabel("λ", fontsize=32)
    plt.ylabel("λ=0 (従来評価関数) との比率", fontsize=32)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # グラフを保存
    plot_path = result_dir / f"{plot_filename_prefix}_ratio_plot.pdf"
    plt.savefig(plot_path, dpi=300)
    print(f"グラフを{plot_path}に保存しました。")
    plt.close()


if __name__ == "__main__":
    summarize_and_plot(Path("results/decay_true"), "decay_true")
    summarize_and_plot(Path("results/decay_false"), "decay_false")
