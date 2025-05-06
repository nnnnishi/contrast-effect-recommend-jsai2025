import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib_fontja

from utils.utils import calculate_user_state_score

# このファイルのディレクトリの親（src）をパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def plot_user_state_score_3d(score_func, filename, decay_flag):
    # グリッドの作成
    max_steps = 100
    x = np.linspace(0, max_steps, 50)  # ph1_count
    y = np.linspace(0, max_steps, 50)  # steps_since_last_ph1
    X, Y = np.meshgrid(x, y)

    # user_state_scoreの計算
    Z = np.zeros_like(X)
    for i in range(len(x)):
        for j in range(len(y)):
            if decay_flag:
                Z[i, j] = score_func(X[i, j], Y[i, j])
            else:
                Z[i, j] = 1

    # プロット作成
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # サーフェスプロット
    surf = ax.plot_surface(X, Y, Z, cmap="viridis", antialiased=True, alpha=0.8)

    # 視点の回転（xy平面で90度）
    ax.view_init(elev=30, azim=150)

    # カラーバーの追加
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, pad=0.1)

    # カラーバーの太さを調整
    cbar.ax.set_box_aspect(20)  # 縦横比を調整
    cbar.outline.set_linewidth(0.5)  # 枠線の太さを調整

    # 軸ラベルの設定
    ax.set_xlabel("オンライン行動数")
    ax.set_ylabel("最終オンライン行動からの経過日数")
    ax.set_zlabel("将来のマッチング率")

    # グラフの保存
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    plot_user_state_score_3d(
        calculate_user_state_score, "img/user_state_score_3d_graph_decay_true.pdf", True
    )
    plot_user_state_score_3d(
        calculate_user_state_score,
        "img/user_state_score_3d_graph_decay_false.pdf",
        False,
    )
