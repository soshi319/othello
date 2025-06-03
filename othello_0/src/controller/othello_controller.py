import numpy as np
import random
import time

BOARD_SIZE = 6

from ..data.black_stones import BlackStones
from ..data.white_stones import WhiteStones
from ..data.can_put_dots import CanPutDots

class Othello:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        c = BOARD_SIZE // 2
        self.board[c-1, c-1] = 1
        self.board[c, c] = 1
        self.board[c-1, c] = 2
        self.board[c, c-1] = 2

        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.turn = 2 # 黒が先手

    def start_game(self):
        c = BOARD_SIZE // 2
        self.flip([(c-1, c-1), (c, c)], 1)
        self.flip([(c-1, c), (c, c-1)], 2)
    
    def put_stone(self, row, column, page):
        # print(f"DEBUG: put_stone called for ({row},{column}). Current turn: {self.turn}")
        # print(f"DEBUG: Board before put:\n{self.board}")
        # print(f"DEBUG: Can_put_area for turn {self.turn}: {self.can_put_area(self.turn)}")

        if not self.can_put_area(self.turn):
            if self.try_pass(page): # try_passの中でpage.update()が呼ばれる
                return
        
        if (row, column) in self.can_put_area(self.turn):
            original_turn = self.turn # 石を置く前の手番を記録
            
            stones_to_flip = self.flip_area(row, column) # この中で self.turn を参照している
            self.flip(stones_to_flip, original_turn) # 置いた石の色で盤面更新
            
            # ターン交代とヒント更新
            if original_turn == 1: # 白が置いた
                self.turn = 2 # 次は黒
                self.can_put_area_unvisible() # 黒の番なのでヒントは消す（AIターン非表示とは別）
            elif original_turn == 2: # 黒が置いた
                self.turn = 1 # 次は白
                self.can_put_area_visible() # 白の番なのでヒントを表示
            
            page.update()

            # ★★★ 石を置いた後、相手がパスするか確認 ★★★
            if not self.can_put_area(self.turn):
                # print(f"DEBUG: Opponent (turn {self.turn}) might need to pass.")
                self.try_pass(page) # try_passの中でターンが変わり、ヒントも更新される
        # else:
            # print(f"DEBUG: Invalid move ({row},{column}) in put_stone. Valid moves: {self.can_put_area(self.turn)}")


    def can_put_area_visible(self):
        # print(f"DEBUG: can_put_area_visible called for turn {self.turn}")
        can_flip_area = self.can_put_area(self.turn)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if hasattr(self.can_put_dots[i][j], 'current') and self.can_put_dots[i][j].current:
                    self.can_put_dots[i][j].current.visible = False

        for row, column in can_flip_area:
            if hasattr(self.can_put_dots[row][column], 'current') and self.can_put_dots[row][column].current:
                self.can_put_dots[row][column].current.visible = True

    def can_put_area_unvisible(self):
        # print(f"DEBUG: can_put_area_unvisible called for turn {self.turn}")
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if hasattr(self.can_put_dots[i][j], 'current') and self.can_put_dots[i][j].current:
                    self.can_put_dots[i][j].current.visible = False

    def can_put_area(self, turn_to_check): # 引数名を turn から turn_to_check に変更
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        possible_moves = []

        for r_idx in range(BOARD_SIZE):
            for c_idx in range(BOARD_SIZE):
                if self.board[r_idx, c_idx] == 0: # 空きマスか
                    can_place_here = False
                    opponent_color = 3 - turn_to_check
                    for dr, dc in directions:
                        stones_in_between = []
                        curr_r, curr_c = r_idx + dr, c_idx + dc
                        while 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and self.board[curr_r, curr_c] == opponent_color:
                            stones_in_between.append((curr_r, curr_c))
                            curr_r += dr
                            curr_c += dc
                        if stones_in_between and 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and self.board[curr_r, curr_c] == turn_to_check:
                            can_place_here = True
                            break 
                    if can_place_here:
                        possible_moves.append((r_idx, c_idx))
        return possible_moves

    def flip_area(self, r_start, c_start): # 引数名を row, column から r_start, c_start に変更
        turn_making_move = self.turn # 現在の実際の手番
        opponent_color = 3 - turn_making_move
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        stones_to_flip_overall = []
        
        # 石を置くマス自体も、最終的にそのプレイヤーの色になるのでリストに含める
        stones_to_flip_overall.append((r_start, c_start))

        for dr, dc in directions:
            current_line_flips = []
            curr_r, curr_c = r_start + dr, c_start + dc

            while 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and self.board[curr_r, curr_c] == opponent_color:
                current_line_flips.append((curr_r, curr_c))
                curr_r += dr
                curr_c += dc
            
            if current_line_flips and 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and self.board[curr_r, curr_c] == turn_making_move:
                stones_to_flip_overall.extend(current_line_flips)
        
        return stones_to_flip_overall


    def flip(self, flip_list, sign):
        for row, column in flip_list:
            self.board[row, column] = sign
            if hasattr(self.white_stones[row][column], 'current') and self.white_stones[row][column].current and \
               hasattr(self.black_stones[row][column], 'current') and self.black_stones[row][column].current:
                if sign == 1:
                    self.white_stones[row][column].current.visible = True
                    self.black_stones[row][column].current.visible = False
                elif sign == 2:
                    self.white_stones[row][column].current.visible = False
                    self.black_stones[row][column].current.visible = True

    def ai_move(self, page):
        possible_moves = self.can_put_area(self.turn)
        if not possible_moves:
            if self.try_pass(page):
                # page.update() # try_passの中で呼ばれるので不要
                return
        if possible_moves:
            time.sleep(0.5)
            row, col = random.choice(possible_moves)
            self.put_stone(row, col, page)
    
    def monte_carlo_ai_move(self, page, num_simulations=500):
        possible_moves = self.can_put_area(self.turn)
        if not possible_moves:
            if self.try_pass(page):
                # page.update()
                return
            
        best_winrate = -1
        best_move = None
        if not possible_moves: return # 念のため

        for r_mc, c_mc in possible_moves:
            win = 0
            for _ in range(num_simulations):
                winner = self.simulate_game_from_move(r_mc, c_mc)
                if winner == self.turn:
                    win += 1
            winrate = win / num_simulations
            # print(f"手 ({r_mc},{c_mc}) の勝率: {winrate:.2f}")
            if winrate > best_winrate:
                best_winrate = winrate
                best_move = (r_mc, c_mc)

        if best_move is not None:
            time.sleep(0.2) 
            self.put_stone(best_move[0], best_move[1], page)
            print("モンテカルロ発動！")

    def simulate_game_from_move(self, r_sim, c_sim): # 引数名を変更
        sim_board = np.copy(self.board)
        sim_turn = self.turn

        self._simulate_put_stone(sim_board, r_sim, c_sim, sim_turn)
        sim_turn = 3 - sim_turn

        passes_in_a_row = 0
        while np.any(sim_board == 0) and passes_in_a_row < 2:
            can_put_sim = self._simulate_can_put_area(sim_board, sim_turn)
            if not can_put_sim:
                sim_turn = 3 - sim_turn
                passes_in_a_row += 1
                if passes_in_a_row >= 2:
                    break
                continue
            
            passes_in_a_row = 0
            move_sim = random.choice(can_put_sim)
            self._simulate_put_stone(sim_board, move_sim[0], move_sim[1], sim_turn)
            sim_turn = 3 - sim_turn

        white_count = np.sum(sim_board == 1)
        black_count = np.sum(sim_board == 2)
        if white_count > black_count: return 1
        elif black_count > white_count: return 2
        else: return 0
        
    def _simulate_put_stone(self, board_s, r_s, c_s, turn_s): # 引数名を変更
        opponent_s = 3 - turn_s
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        board_s[r_s, c_s] = turn_s
        for dr_s, dc_s in directions:
            stones_to_flip_in_line = []
            curr_r, curr_c = r_s + dr_s, c_s + dc_s
            while 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and board_s[curr_r, curr_c] == opponent_s:
                stones_to_flip_in_line.append((curr_r, curr_c))
                curr_r += dr_s
                curr_c += dc_s
            if stones_to_flip_in_line and 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and board_s[curr_r, curr_c] == turn_s:
                for r_f, c_f in stones_to_flip_in_line:
                    board_s[r_f, c_f] = turn_s

    def _simulate_can_put_area(self, board_s, turn_s): # 引数名を変更
        opponent_s = 3 - turn_s
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        possible_moves_s = []
        for r_idx_s in range(BOARD_SIZE):
            for c_idx_s in range(BOARD_SIZE):
                if board_s[r_idx_s, c_idx_s] == 0:
                    can_place_here_s = False
                    for dr_s, dc_s in directions:
                        stones_in_between_s = []
                        curr_r, curr_c = r_idx_s + dr_s, c_idx_s + dc_s
                        while 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and board_s[curr_r, curr_c] == opponent_s:
                            stones_in_between_s.append((curr_r, curr_c))
                            curr_r += dr_s
                            curr_c += dc_s
                        if stones_in_between_s and 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and board_s[curr_r, curr_c] == turn_s:
                            can_place_here_s = True
                            break
                    if can_place_here_s:
                        possible_moves_s.append((r_idx_s, c_idx_s))
        return possible_moves_s
    
    def try_pass(self, page):
        # print(f"DEBUG: try_pass called for turn {self.turn}")
        if not self.can_put_area(self.turn): # 現在のターンのプレイヤーが本当に置けないか確認
            current_player_name = "白" if self.turn == 1 else "黒"
            print(f"{current_player_name}の番: 置ける場所がないためパスします。")
            
            self.turn = 3 - self.turn  # ターン交代
            
            # ★★★ ターン交代後のヒント表示 ★★★
            if self.turn == 1: # 白番になった
                self.can_put_area_visible()
            else: # 黒番になった
                self.can_put_area_unvisible()
            page.update()

            # 交代後の相手も置けないか確認 (ゲーム終了条件)
            if not self.can_put_area(self.turn):
                next_player_name = "白" if self.turn == 1 else "黒"
                print(f"{next_player_name}も置けません。両者ともパスとなり、ゲーム終了です。")
                self.end_game(page)
            return True  # パス処理が行われた
        return False # パスしなかった
    
    def end_game(self, page):
        white_count = np.sum(self.board == 1)
        black_count = np.sum(self.board == 2)
        print(f"ゲーム終了！ 白: {white_count}  黒: {black_count}")
        result_message = ""
        if white_count > black_count: result_message = "白の勝ち！"
        elif white_count < black_count: result_message = "黒の勝ち！"
        else: result_message = "引き分け！"
        print(result_message)
        # (オプション) Fletのダイアログなどで結果を表示する