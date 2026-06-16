import time

import settings
from data.records_manager import save_record
from ai.easy_ai import EasyAI
from ai.normal_ai import NormalAI
from ai.hard_ai import HardAI
from ai.master_ai import MasterAI


class Othello:
    def __init__(self, white_stones, black_stones, can_put_dots, ai_player_number=None, view_ref=None):
        self.white_stones = white_stones
        self.black_stones = black_stones
        self.can_put_dots = can_put_dots
        self.ai_player_number = ai_player_number
        self.view_ref = view_ref

        self.turn = 1
        self.ai_move_count = 0

        # 8*8
        if settings.BOARD_SIZE == 8:
            self.MASK_ALL = (1 << 64) - 1
            mask_col_a = sum(1 << (row * 8) for row in range(8))
            mask_col_h = sum(1 << (row * 8 + 7) for row in range(8))
            self.MASK_COL_LEFT = self.MASK_ALL & ~mask_col_a
            self.MASK_COL_RIGHT = self.MASK_ALL & ~mask_col_h

            self.DIRECTIONS = [
                (1, self.MASK_COL_LEFT, True),   # 右
                (1, self.MASK_COL_RIGHT, False), # 左
                (8, self.MASK_ALL, True),        # 下
                (8, self.MASK_ALL, False),       # 上
                (9, self.MASK_COL_LEFT, True),   # 右下
                (9, self.MASK_COL_RIGHT, False), # 左上
                (7, self.MASK_COL_RIGHT, True),  # 左下
                (7, self.MASK_COL_LEFT, False)   # 右上
            ]

            self.black_board = (1 << 28) | (1 << 35)
            self.white_board = (1 << 27) | (1 << 36)

            self.weights = [
                [30, -12,  0, -1, -1,  0, -12, 30],
                [-12, -15, -3, -3, -3, -3, -15, -12],
                [ 0,  -3,  0, -1, -1,  0,  -3,  0],
                [-1,  -3, -1, -1, -1, -1,  -3, -1],
                [-1,  -3, -1, -1, -1, -1,  -3, -1],
                [ 0,  -3,  0, -1, -1,  0,  -3,  0],
                [-12, -15, -3, -3, -3, -3, -15, -12],
                [30, -12,  0, -1, -1,  0, -12, 30]
            ]

        # 6*6
        elif settings.BOARD_SIZE == 6:
            self.MASK_ALL = (1 << 36) - 1
            
            mask_col_a = sum(1 << (row * 6) for row in range(6))
            mask_col_f = sum(1 << (row * 6 + 5) for row in range(6))
            self.MASK_COL_LEFT = self.MASK_ALL ^ mask_col_a
            self.MASK_COL_RIGHT = self.MASK_ALL ^ mask_col_f
            
            self.DIRECTIONS = [
                (1, self.MASK_COL_LEFT, True),
                (1, self.MASK_COL_RIGHT, False),
                (6, self.MASK_ALL, True),
                (6, self.MASK_ALL, False),
                (7, self.MASK_COL_LEFT, True),
                (7, self.MASK_COL_RIGHT, False),
                (5, self.MASK_COL_RIGHT, True),
                (5, self.MASK_COL_LEFT, False)
            ]
            
            self.black_board = (1 << 15) | (1 << 20)
            self.white_board = (1 << 14) | (1 << 21)

            self.weights = [
                [30, -12,  0,  0, -12, 30],
                [-12, -15, -3, -3, -15, -12],
                [ 0,  -3,  0,  0,  -3,  0],
                [ 0,  -3,  0,  0,  -3,  0],
                [-12, -15, -3, -3, -15, -12],
                [30, -12,  0,  0, -12, 30]
            ]

        self.easy_ai = EasyAI(self)
        self.normal_ai = NormalAI(self)
        self.hard_ai = HardAI(self)
        self.master_ai = MasterAI(self)



    # ==========================================
    # ブリッジ関数
    # ==========================================
    def rc_to_bit(self, row, col):
        pos = row * settings.BOARD_SIZE + col
        return 1 << pos

    def bit_to_rc(self, bit_mask):
        if bit_mask == 0:
            return None
        pos = bit_mask.bit_length() - 1
        row = pos // settings.BOARD_SIZE
        col = pos % settings.BOARD_SIZE
        return row, col

    # ==========================================
    # コア演算・ゲーム進行ルーチン
    # ==========================================
    def start_game(self):
        legal_board = self.get_legal_moves(self.black_board, self.white_board)
        if self.view_ref:
            self.view_ref.render_board(self.black_board, self.white_board, legal_board)

    def get_legal_moves(self, player_board, opponent_board):
        legal_board = 0
        empty_board = ~(player_board | opponent_board) & self.MASK_ALL

        for shift, mask, is_left in self.DIRECTIONS:
            if is_left:
                temp = (player_board << shift) & mask & opponent_board
            else:
                temp = (player_board >> shift) & mask & opponent_board
            
            max_flip = settings.BOARD_SIZE - 2
            for _ in range(max_flip):
                if is_left:
                    temp |= (temp << shift) & mask & opponent_board
                else:
                    temp |= (temp >> shift) & mask & opponent_board
            
            if is_left:
                legal_board |= (temp << shift) & mask & empty_board
            else:
                legal_board |= (temp >> shift) & mask & empty_board

        return legal_board

    # ==========================================
    # AIを選択して打たせる
    # ==========================================
    def execute_ai_move_by_difficulty(self, difficulty, page):
        """難易度に応じて適切なAIを選択し、思考させて着手を実行する"""
        # 思考開始の時間を記録
        start_time = time.time()
        
        move_bit = None

        if difficulty == "easy":
            move_bit = self.easy_ai.get_move()
        elif difficulty == "normal":
            move_bit = self.normal_ai.get_move()
        elif difficulty == "hard":
            move_bit = self.hard_ai.get_move()
        elif difficulty == "master":
            move_bit = self.master_ai.get_move()
        elif difficulty == "ucb":
            move_bit = self.ucb_ai.get_move()
        elif difficulty == "oni":
            move_bit = self.dqn_ai.get_move()

        elapsed_time = time.time() - start_time
        print(elapsed_time)
        
        # もし計算が早すぎたら、settingsで設定した秒数になるまで待機（スリープ）する
        if elapsed_time < settings.AI_WAIT_TIME:
            time.sleep(settings.AI_WAIT_TIME - elapsed_time)

        if move_bit:
            row, col = self.bit_to_rc(move_bit)
            self.put_stone(row, col, page)
            self.ai_move_count += 1
        else:
            self.try_pass(page)

    # ==========================================
    # 石を置く・パス・終局判定（ゲーム進行処理）
    # ==========================================
    def get_flipped_board(self, move_bit, player_board, opponent_board):
        """指定した場所に石を置いたとき、裏返る石を計算する"""
        flipped_stones = 0
        for shift, mask, is_left in self.DIRECTIONS:
            temp_flipped = 0
            if is_left:
                temp = (move_bit << shift) & mask & opponent_board
            else:
                temp = (move_bit >> shift) & mask & opponent_board

            while temp != 0:
                temp_flipped |= temp
                if is_left:
                    temp = (temp << shift) & mask & opponent_board
                else:
                    temp = (temp >> shift) & mask & opponent_board

            if is_left:
                is_ok = (temp_flipped << shift) & mask & player_board
            else:
                is_ok = (temp_flipped >> shift) & mask & player_board

            if is_ok != 0:
                flipped_stones |= temp_flipped
        return flipped_stones


    def put_stone(self, row, col, page):
        """実際に石を置き、盤面を更新する"""
        move_bit = self.rc_to_bit(row, col)

        if self.turn == 1:
            player_board = self.black_board
            opponent_board = self.white_board
        else:
            player_board = self.white_board
            opponent_board = self.black_board

        legal_board = self.get_legal_moves(player_board, opponent_board)
        if (move_bit & legal_board) == 0:
            return False

        flipped = self.get_flipped_board(move_bit, player_board, opponent_board)

        # 盤面の更新 (自分の石は追加=OR、相手の石は反転=XOR)
        if self.turn == 1:
            self.black_board |= move_bit | flipped
            self.white_board ^= flipped
        else:
            self.white_board |= move_bit | flipped
            self.black_board ^= flipped


        self.turn = 3 - self.turn

        next_p_board = self.black_board if self.turn == 1 else self.white_board
        next_o_board = self.white_board if self.turn == 1 else self.black_board
        next_legal_board = self.get_legal_moves(next_p_board, next_o_board)

        if self.view_ref:
            self.view_ref.render_board(self.black_board, self.white_board, next_legal_board)

        self.check_game_state(next_legal_board, page)
        return True


    def try_pass(self, page):
        """パス処理を行い、ターンを飛ばす"""
        if self.view_ref:
            self.view_ref.show_pass_ui()

        self.turn = 3 - self.turn

        next_p_board = self.black_board if self.turn == 1 else self.white_board
        next_o_board = self.white_board if self.turn == 1 else self.black_board
        next_legal_board = self.get_legal_moves(next_p_board, next_o_board)

        if self.view_ref:
            self.view_ref.render_board(self.black_board, self.white_board, next_legal_board)

        self.check_game_state(next_legal_board, page)


    def check_game_state(self, current_legal_board, page):
        """現在のターンで打てる場所がない場合、パスか終局かを判定する"""
        if current_legal_board == 0:
            opp_p_board = self.white_board if self.turn == 1 else self.black_board
            opp_o_board = self.black_board if self.turn == 1 else self.white_board
            opp_legal_board = self.get_legal_moves(opp_p_board, opp_o_board)

            if opp_legal_board == 0:
                black_count = bin(self.black_board).count('1')
                white_count = bin(self.white_board).count('1')

                # AI同士の対戦でない場合のみ記録を保存
                is_ai_vs_ai = getattr(self.view_ref, 'is_ai_vs_ai', False) if self.view_ref else False
                if not is_ai_vs_ai and self.ai_player_number is not None:
                    difficulty = getattr(self.view_ref, 'level', None) if self.view_ref else None
                    if difficulty:
                        player_is_black = (self.ai_player_number == 2)
                        player_count = black_count if player_is_black else white_count
                        ai_count = white_count if player_is_black else black_count
                        if player_count > ai_count:
                            save_record(difficulty, "win")
                        elif player_count < ai_count:
                            save_record(difficulty, "lose")
                        else:
                            save_record(difficulty, "draw")

                elif is_ai_vs_ai:
                    from data.records_manager import save_ai_match_record
                    
                    # ページに保存されている両AIの難易度を取得
                    black_level = getattr(self.view_ref.page, 'ai_black_level', None)
                    white_level = getattr(self.view_ref.page, 'ai_white_level', None)
                    
                    if black_level and white_level:
                        if black_count > white_count:
                            save_ai_match_record(black_level, white_level, 1) # 黒の勝ち
                        elif white_count > black_count:
                            save_ai_match_record(black_level, white_level, 2) # 白の勝ち
                        else:
                            save_ai_match_record(black_level, white_level, 0) # 引き分け

                if self.view_ref:
                    self.view_ref.show_result_ui(white_count, black_count)
            else:
                self.try_pass(page)

    

    def run_fast_match(self, black_difficulty, white_difficulty, page):
        """UI描画やウェイトを完全に無効化して、裏で1試合を高速シミュレーションする"""
        import settings
        # 設定とview_refの退避（後で元に戻すため）
        old_wait = settings.AI_WAIT_TIME
        settings.AI_WAIT_TIME = 0.0  # AIの思考ウェイトをゼロにする
        old_view = self.view_ref
        self.view_ref = None  # 描画処理をスキップさせる
        
        # ゲームの初期化
        if hasattr(self, "start_game"):
            self.start_game()
        else:
            # start_gameがない場合の予備初期化
            self.turn = 1
            if settings.BOARD_SIZE == 8:
                self.black_board = 0x0000001008000000
                self.white_board = 0x0000000810000000
            else:
                self.black_board = 0x0000040800000000 >> 9
            self.game_over = False

        self.game_over = False
        
        # 終局（game_over = True）になるまでループを回す
        while not self.game_over:
            current_diff = black_difficulty if self.turn == 1 else white_difficulty
            self.execute_ai_move_by_difficulty(current_diff, page)
            
        # 最終的な石の数をカウント
        black_count = bin(self.black_board).count('1')
        white_count = bin(self.white_board).count('1')
        
        # 元の設定状態に復元
        settings.AI_WAIT_TIME = old_wait
        self.view_ref = old_view
        
        # 戻り値: 1=黒番勝ち, 2=白番勝ち, 0=引き分け
        if black_count > white_count:
            return 1
        elif white_count > black_count:
            return 2
        else:
            return 0
        
        # (クラス内の他のメソッドはそのまま)

    # ==========================================
    # [追記] 形勢評価（有利不利の数値化）
    # ==========================================
    def get_evaluation_score(self):
        """
        現在の盤面の評価値を計算する（黒の評価重みの合計 - 白の評価重みの合計）。
        プラスなら黒有利、マイナスなら白有利となる。
        """
        black_score = 0
        white_score = 0
        size = settings.BOARD_SIZE
        
        for row in range(size):
            for col in range(size):
                pos = row * size + col
                mask = 1 << pos
                if self.black_board & mask:
                    black_score += self.weights[row][col]
                elif self.white_board & mask:
                    white_score += self.weights[row][col]
                    
        return black_score - white_score