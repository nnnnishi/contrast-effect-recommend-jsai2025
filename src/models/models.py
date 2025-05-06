from dataclasses import dataclass


@dataclass
class User:
    """ユーザクラス"""

    id: int
    ph1_count: int = 0
    last_ph1_step: int = 0
    finished: bool = False


@dataclass
class Item:
    """アイテムクラス"""

    user: int
    step: int
    item: int
    ph1_score: float
    ph2_score: float
    ph3_score: float
