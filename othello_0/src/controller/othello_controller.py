# othello_controller.py (ファイル26の修正案)
import numpy as np
import random
import time

BOARD_SIZE = 6

from ..data.black_stones import BlackStones
from ..data.white_stones import WhiteStones
from ..data.can_put_dots import CanPutDots

class Othello:
    def __init__(self, ai_player_number=None): # ai_player_number を受け取る
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        c = BOARD_SIZE // 2
        self.board[c-1, c-1] = 1
        self.board[c, c] = 1
        self.board[c-1, c] = 2
        self.board[c, c-1] = 2

        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots

        self.turn = 2 # 黒(2)からスタート
        self.ai_player_number = ai_player_number # AIのプレイヤー番号を保持

    def start_game(self):
        c = BOARD_SIZE // 2
        self.flip([(c-1, c-1), (c, c)], 1)
        self.flip([(c-1, c), (c, c-1)], 2)
        # ゲーム開始時のヒント表示は update_can_put_dots_display に任せる
        # self.can_put_area_visible() # 古い呼び出しは削除

    def update_can_put_dots_display(self):
        """現在のターンのヒント表示を更新。AIのターンでは表示しない。"""
        # まず全てのドットを非表示にする
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.can_put_dots[i][j] and hasattr(self.can_put_dots[i][j], 'current') and self.can_put_dots[i][j].current:
                    self.can_put_dots[i][j].current.visible = False

        # 現在のターンがAIのターンかどうかを判定
        is_ai_turn = self.ai_player_number is not None and self.turn == self.ai_player_number
        
        print(f"DEBUG CONTROLLER: update_can_put_dots_display - Current Turn: {self.turn}, AI Player Num: {self.ai_player_number}, Is AI Turn: {is_ai_turn}") # デバッグ追加

        if not is_ai_turn: # AIのターンでなければ (つまりプレイヤーのターンなら) ヒントを表示
            possible_moves = self.can_put_area(self.turn)
            print(f"DEBUG CONTROLLER: Player's turn, possible_moves: {possible_moves}") # デバッグ追加
            for row, column in possible_moves:
                if self.can_put_dots[row][column] and hasattr(self.can_put_dots[row][column], 'current') and self.can_put_dots[row][column].current:
                    self.can_put_dots[row][column].current.visible = True
        else:
            print(f"DEBUG CONTROLLER: AI's turn, no dots will be shown.") # デバッグ追加
  
    def put_stone(self, row, column, page):
        if not self.can_put_area(self.turn):
            if self.try_pass(page):
                return
        
        if (row, column) in self.can_put_area(self.turn):
            player_making_move = self.turn
            stones_to_flip = self.flip_area(row, column)
            self.flip(stones_to_flip, player_making_move)
            
            self.turn = 3 - player_making_move # ターン交代
            
            self.update_can_put_dots_display() # ★修正: 新しいヒント表示メソッドを呼び出す
            page.update()

            if not self.can_put_area(self.turn):
                self.try_pass(page)
        else:
            print(f"警告: ({row}, {column}) への配置は無効と判定されました。現在のターン: {self.turn}")
            print(f"有効な手: {self.can_put_area(self.turn)}")

    # can_put_area_visible と can_put_area_unvisible は update_can_put_dots_display に統合されたため削除
    # def can_put_area_visible(self): ...
    # def can_put_area_unvisible(self): ...

    def can_put_area(self, turn_to_check):
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        possible_moves = [] 
        for r_idx in range(BOARD_SIZE):
            for c_idx in range(BOARD_SIZE):
                if self.board[r_idx, c_idx] == 0: 
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

    def flip_area(self, r_start, c_start):
        turn_making_move = self.turn
        opponent_color = 3 - turn_making_move
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        stones_to_flip_overall = [] 
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
                return 
        if possible_moves: 
            time.sleep(0.5)
            row, col = random.choice(possible_moves)
            self.put_stone(row, col, page)
    
    def monte_carlo_ai_move(self, page, num_simulations=500):
        possible_moves = self.can_put_area(self.turn)
        if not possible_moves:
            if self.try_pass(page):
                return
        best_winrate = -1
        best_move = None
        if not possible_moves: return
        for r_mc, c_mc in possible_moves:
            win = 0
            for _ in range(num_simulations):
                winner = self.simulate_game_from_move(r_mc, c_mc)
                if winner == self.turn:
                    win += 1
            winrate = win / num_simulations
            if winrate > best_winrate:
                best_winrate = winrate
                best_move = (r_mc, c_mc)
        if best_move is not None:
            time.sleep(0.2) 
            self.put_stone(best_move[0], best_move[1], page)
            print("モンテカルロ発動！")

    def simulate_game_from_move(self, r_sim, c_sim):
        sim_board = np.copy(self.board)
        sim_turn = self.turn
        self._simulate_put_stone(sim_board, r_sim, c_sim, sim_turn)
        sim_turn = 3 - sim_turn
        passes_in_a_row = 0 
        while np.any(sim_board == 0) and passes_in_a_row < 2:
            can_put_sim = self._simulate_can_put_area(sim_board, sim_turn)
            if not can_put_sim:
                sim_turn = 3 - sim_turn
                passes_in_a_row +=1
                if passes_in_a_row >= 2: break 
                continue 
            passes_in_a_row = 0 
            move_sim = random.choice(can_put_sim)
            self._simulate_put_stone(sim_board, move_sim[0], move_sim[1], sim_turn)
            sim_turn = 3 - sim_turn
        white_count = np.sum(sim_board == 1)
        black_count = np.sum(sim_board == 2)
        if self.turn == 1: # 元の手番が白（AI）だった場合
            if white_count > black_count: return 1 
            elif black_count > white_count: return 2 
            else: return 0 
        elif self.turn == 2: # 元の手番が黒（AI）だった場合
            if black_count > white_count: return 2 
            elif white_count > black_count: return 1 
            else: return 0 
        return 0 
        
    def _simulate_put_stone(self, board_s, r_s, c_s, turn_s):
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

    def _simulate_can_put_area(self, board_s, turn_s):
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
        if not self.can_put_area(self.turn): 
            current_player_name = "白" if self.turn == 1 else "黒"
            print(f"{current_player_name}の番: 置ける場所がないためパスします。")
            
            self.turn = 3 - self.turn  
            self.update_can_put_dots_display() # ★修正: 新しいヒント表示メソッドを呼び出す
            page.update()

            if not self.can_put_area(self.turn):
                next_player_name = "白" if self.turn == 1 else "黒"
                print(f"{next_player_name}も置けません。両者ともパスとなり、ゲーム終了です。")
                self.end_game(page) 
            return True  
        return False 
    
    def end_game(self, page_arg_ctrl):
        white_count = np.sum(self.board == 1)
        black_count = np.sum(self.board == 2)
        
        print(f"DEBUG CONTROLLER: end_game called. White: {white_count}, Black: {black_count}. Page ID: {id(page_arg_ctrl)}")

        current_view_instance = page_arg_ctrl.views[-1] 

        if hasattr(current_view_instance, 'show_result_dialog') and callable(getattr(current_view_instance, 'show_result_dialog')):
            print(f"DEBUG CONTROLLER: Found callable current_view_instance.show_result_dialog. Calling it.")
            current_view_instance.show_result_dialog(white_count, black_count, page_arg_ctrl) 
        else:
            print(f"DEBUG CONTROLLER: current_view_instance.show_result_dialog not found or not callable.")
            print(f"ゲーム終了！ 白: {white_count}  黒: {black_count}")
            if white_count > black_count: print("白の勝ち！")
            elif black_count > white_count: print("黒の勝ち！")
            else: print("引き分け！")