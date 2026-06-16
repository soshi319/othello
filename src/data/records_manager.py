import json
import os

RECORDS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "records.json")

DIFFICULTIES = ["easy", "normal", "hard", "master", "oni"]

def _get_records_path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "data", "records.json")

def load_records():
    path = _get_records_path()
    if not os.path.exists(path):
        return {d: {"win": 0, "lose": 0, "draw": 0} for d in DIFFICULTIES}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 欠けているキーを補完
        for d in DIFFICULTIES:
            if d not in data:
                data[d] = {"win": 0, "lose": 0, "draw": 0}
            for k in ["win", "lose", "draw"]:
                if k not in data[d]:
                    data[d][k] = 0
        return data
    except Exception:
        return {d: {"win": 0, "lose": 0, "draw": 0} for d in DIFFICULTIES}

def save_record(difficulty, result):
    """
    difficulty: "easy" / "normal" / "hard" / "master" / "oni"
    result: "win" / "lose" / "draw"
    """
    if difficulty not in DIFFICULTIES:
        return
    if result not in ("win", "lose", "draw"):
        return
    data = load_records()
    data[difficulty][result] += 1
    path = _get_records_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clear_records():
    data = {d: {"win": 0, "lose": 0, "draw": 0} for d in DIFFICULTIES}
    path = _get_records_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# AI vs AI 用の記録管理機能（総当たり表対応版）
# ==========================================
def _get_ai_records_path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "data", "ai_records.json")

def load_ai_records():
    path = _get_ai_records_path()
    
    # 2次元の初期データ構造を作成（黒[先攻] -> 白[後攻]）
    default_data = {}
    for b in DIFFICULTIES:
        default_data[b] = {}
        for w in DIFFICULTIES:
            default_data[b][w] = {"win": 0, "lose": 0, "draw": 0}

    if not os.path.exists(path):
        return default_data
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 前回の古いデータ形式（1次元）が残っていた場合は初期化してエラーを回避
        if "easy" in data and "win" in data["easy"] and isinstance(data["easy"]["win"], int):
            return default_data
            
        # 欠けているキーを補完
        for b in DIFFICULTIES:
            if b not in data: data[b] = {}
            for w in DIFFICULTIES:
                if w not in data[b]: data[b][w] = {"win": 0, "lose": 0, "draw": 0}
                for k in ["win", "lose", "draw"]:
                    if k not in data[b][w]: data[b][w][k] = 0
        return data
    except Exception:
        return default_data

def save_ai_match_record(black_diff, white_diff, result):
    """
    AI同士の対戦結果を保存する
    result: 1(黒勝ち), 2(白勝ち), 0(引き分け)
    """
    if black_diff not in DIFFICULTIES or white_diff not in DIFFICULTIES:
        return
    
    data = load_ai_records()
    
    if black_diff == white_diff:
        # 同キャラ対決：合算すると勝率が必ず50%になるため、例外的に黒番(先攻)視点で記録
        if result == 1:
            data[black_diff][white_diff]["win"] += 1
        elif result == 2:
            data[black_diff][white_diff]["lose"] += 1
        else:
            data[black_diff][white_diff]["draw"] += 1
    else:
        # 異なるAI対決：両方の視点から結果をクロスして記録（合算）
        if result == 1:
            data[black_diff][white_diff]["win"] += 1
            data[white_diff][black_diff]["lose"] += 1
        elif result == 2:
            data[black_diff][white_diff]["lose"] += 1
            data[white_diff][black_diff]["win"] += 1
        else:
            data[black_diff][white_diff]["draw"] += 1
            data[white_diff][black_diff]["draw"] += 1
            
    path = _get_ai_records_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    data = load_ai_records()
    
    # 先攻（黒）視点での勝ち負けを記録
    if result == 1:
        data[black_diff][white_diff]["win"] += 1
    elif result == 2:
        data[black_diff][white_diff]["lose"] += 1
    else:
        data[black_diff][white_diff]["draw"] += 1
        
    path = _get_ai_records_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clear_ai_records():
    default_data = {}
    for b in DIFFICULTIES:
        default_data[b] = {}
        for w in DIFFICULTIES:
            default_data[b][w] = {"win": 0, "lose": 0, "draw": 0}
            
    path = _get_ai_records_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(default_data, f, ensure_ascii=False, indent=2)