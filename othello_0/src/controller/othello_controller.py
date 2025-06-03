# othello_controller.py (ファイル31の修正案)
import numpy as np
import random
import time

BOARD_SIZE = 6

from ..data.black_stones import BlackStones
from ..data.white_stones import WhiteStones
from ..data.can_put_dots import CanPutDots

class Othello:
    def __init__(self, ai_player_number=None):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        c = BOARD_SIZE // 2
        self.board[c-1, c-1] = 1; self.board[c, c] = 1
        self.board[c-1, c] = 2; self.board[c, c-1] = 2
        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.turn = 2
        self.ai_player_number = ai_player_number
        print(f"DEBUG CONTROLLER __init__: Turn: {self.turn}, AI Player Num: {self.ai_player_number}")

    def start_game(self):
        print("DEBUG CONTROLLER: start_game called")
        c = BOARD_SIZE // 2
        self.flip([(c-1, c-1), (c, c)], 1)
        self.flip([(c-1, c), (c, c-1)], 2)
        # ヒント表示は GameView の on_click_start_game 内で update_can_put_dots_display を呼び出す

    def update_can_put_dots_display(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.can_put_dots[i][j] and hasattr(self.can_put_dots[i][j], 'current') and self.can_put_dots[i][j].current:
                    self.can_put_dots[i][j].current.visible = False
        is_ai_turn = self.ai_player_number is not None and self.turn == self.ai_player_number
        print(f"DEBUG CONTROLLER: update_can_put_dots_display - Turn: {self.turn}, AI Num: {self.ai_player_number}, Is AI: {is_ai_turn}")
        if not is_ai_turn:
            possible_moves = self.can_put_area(self.turn)
            print(f"DEBUG CONTROLLER: Player's turn, possible_moves: {possible_moves}")
            for row, column in possible_moves:
                if self.can_put_dots[row][column] and hasattr(self.can_put_dots[row][column], 'current') and self.can_put_dots[row][column].current:
                    self.can_put_dots[row][column].current.visible = True
  
    def put_stone(self, row, column, page):
        print(f"DEBUG CONTROLLER: put_stone trying for ({row},{column}). Current Turn: {self.turn}")
        current_possible_moves = self.can_put_area(self.turn)
        print(f"DEBUG CONTROLLER: put_stone - Possible moves for turn {self.turn}: {current_possible_moves}")

        if not current_possible_moves:
            print(f"DEBUG CONTROLLER: put_stone - No moves for turn {self.turn}. Trying pass.")
            if self.try_pass(page): return
            else:
                print(f"DEBUG CONTROLLER: put_stone - Cannot pass and no moves for turn {self.turn}. This should be game over.")
                return 
        
        if (row, column) in current_possible_moves:
            print(f"DEBUG CONTROLLER: put_stone - Valid move at ({row},{column}) for turn {self.turn}.")
            player_making_move = self.turn
            stones_to_flip = self.flip_area(row, column)
            print(f"DEBUG CONTROLLER: put_stone - Stones to flip: {stones_to_flip}")
            self.flip(stones_to_flip, player_making_move)
            
            self.turn = 3 - player_making_move
            print(f"DEBUG CONTROLLER: put_stone - Turn changed to: {self.turn}")
            
            self.update_can_put_dots_display()
            # GameView側でターン表示を更新させるため、GameViewインスタンスのメソッドを呼ぶ
            if hasattr(page, 'current_game_view_instance') and \
               hasattr(page.current_game_view_instance, 'update_turn_indicator'):
                page.current_game_view_instance.update_turn_indicator()
            
            if page: page.update()

            if not self.can_put_area(self.turn):
                print(f"DEBUG CONTROLLER: put_stone - Next turn ({self.turn}) has no moves. Trying pass.")
                self.try_pass(page)
            print(f"DEBUG CONTROLLER: put_stone for ({row},{column}) finished.")
        else:
            print(f"DEBUG CONTROLLER: put_stone - INVALID MOVE ({row}, {column}). Valid: {current_possible_moves}")

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
        print(f"DEBUG CONTROLLER: flip called with sign {sign} for stones: {flip_list}")
        if not self.white_stones or not self.black_stones or \
           not all(all(ws_ref and hasattr(ws_ref, 'current') for ws_ref in row_refs) for row_refs in self.white_stones) or \
           not all(all(bs_ref and hasattr(bs_ref, 'current') for bs_ref in row_refs) for row_refs in self.black_stones):
            print("DEBUG CONTROLLER: ERROR - stone refs not fully initialized in flip.")
            return

        for row, column in flip_list:
            self.board[row, column] = sign
            if self.white_stones[row][column].current and self.black_stones[row][column].current:
                if sign == 1: # White
                    self.white_stones[row][column].current.visible = True
                    self.black_stones[row][column].current.visible = False
                elif sign == 2: # Black
                    self.white_stones[row][column].current.visible = False
                    self.black_stones[row][column].current.visible = True
            else:
                print(f"DEBUG CONTROLLER: ERROR - Ref not resolved for stone at ({row},{column}) in flip.")
        print(f"DEBUG CONTROLLER: Board after flip:\n{self.board}")

    def ai_move(self, page):
        print(f"DEBUG CONTROLLER: ai_move (random) called for turn {self.turn}")
        possible_moves = self.can_put_area(self.turn)
        print(f"DEBUG CONTROLLER: AI (random) possible_moves: {possible_moves}")
        if not possible_moves:
            print(f"DEBUG CONTROLLER: AI (random) has no moves. Trying to pass.")
            if self.try_pass(page): return 
            else:
                print(f"DEBUG CONTROLLER: AI (random) cannot pass and has no moves.")
                return
        
        if possible_moves: 
            time.sleep(0.5)
            row, col = random.choice(possible_moves)
            print(f"DEBUG CONTROLLER: AI (random) chose ({row},{col})")
            self.put_stone(row, col, page)
            print(f"DEBUG CONTROLLER: ai_move (random) finished for turn {self.turn} (after put_stone)")
    
    def monte_carlo_ai_move(self, page, num_simulations=50): 
        print(f"DEBUG CONTROLLER: monte_carlo_ai_move called for turn {self.turn}. Sims: {num_simulations}")
        possible_moves = self.can_put_area(self.turn)
        print(f"DEBUG CONTROLLER: AI (Monte Carlo) possible_moves for turn {self.turn}: {possible_moves}")
        
        if not possible_moves:
            print(f"DEBUG CONTROLLER: AI (Monte Carlo) has no moves for turn {self.turn}. Trying to pass.")
            if self.try_pass(page): return
            else:
                print(f"DEBUG CONTROLLER: AI (Monte Carlo) cannot pass and has no moves for turn {self.turn}.")
                return
            
        best_winrate = -1
        best_move = None

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
        
        print(f"DEBUG CONTROLLER: AI (Monte Carlo) evaluated moves. Best move: {best_move} with win_rate: {best_winrate}")

        if best_move is not None:
            print(f"DEBUG CONTROLLER: AI (Monte Carlo) is putting stone at ({best_move[0]},{best_move[1]})")
            self.put_stone(best_move[0], best_move[1], page) # この中でターン表示も更新されるはず
            print(f"DEBUG CONTROLLER: monte_carlo_ai_move finished for turn {self.turn} (after put_stone)")
        else:
            print("DEBUG CONTROLLER: AI (Monte Carlo) could not determine a best move. THIS SHOULD NOT HAPPEN if possible_moves is not empty.")
            if possible_moves:
                 print("DEBUG CONTROLLER: AI (Monte Carlo) falling back to random move.")
                 row, col = random.choice(possible_moves)
                 self.put_stone(row, col, page)
                 print(f"DEBUG CONTROLLER: monte_carlo_ai_move (fallback) finished for turn {self.turn} (after put_stone)")
            else: 
                print("DEBUG CONTROLLER: AI (Monte Carlo) fallback also has no moves. Critical error or game already ended.")

    def simulate_game_from_move(self, r_sim, c_sim):
        sim_board = np.copy(self.board)
        current_sim_turn = self.turn 
        self._simulate_put_stone(sim_board, r_sim, c_sim, current_sim_turn)
        current_sim_turn = 3 - current_sim_turn 
        passes_in_a_row = 0
        while np.any(sim_board == 0) and passes_in_a_row < 2:
            possible_moves_sim = self._simulate_can_put_area(sim_board, current_sim_turn)
            if not possible_moves_sim:
                current_sim_turn = 3 - current_sim_turn
                passes_in_a_row += 1
                if passes_in_a_row >= 2: break 
                continue 
            passes_in_a_row = 0
            move_sim = random.choice(possible_moves_sim)
            self._simulate_put_stone(sim_board, move_sim[0], move_sim[1], current_sim_turn)
            current_sim_turn = 3 - current_sim_turn
        white_count = np.sum(sim_board == 1)
        black_count = np.sum(sim_board == 2)
        if self.turn == 1: 
            if white_count > black_count: return 1 
            elif black_count > white_count: return 2 
            else: return 0 
        elif self.turn == 2: 
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
    
    def try_pass(self, page_arg_ctrl): # 引数名を page -> page_arg_ctrl に統一
        current_turn_before_pass = self.turn
        print(f"DEBUG CONTROLLER: try_pass called for turn {current_turn_before_pass}")
        
        if not self.can_put_area(current_turn_before_pass): 
            current_player_name = "白" if current_turn_before_pass == 1 else "黒"
            print(f"{current_player_name}の番: 置ける場所がないためパスします。")
            
            self.turn = 3 - current_turn_before_pass  
            print(f"DEBUG CONTROLLER: Turn changed to {self.turn} after {current_player_name}'s pass.")
            
            self.update_can_put_dots_display() 
            
            # ★★★ GameView側のターン表示も更新 ★★★
            if hasattr(page_arg_ctrl, 'current_game_view_instance') and \
               hasattr(page_arg_ctrl.current_game_view_instance, 'update_turn_indicator'):
                print("DEBUG CONTROLLER: Calling game_view.update_turn_indicator() from try_pass")
                page_arg_ctrl.current_game_view_instance.update_turn_indicator()
            else:
                print("DEBUG CONTROLLER: Could not call game_view.update_turn_indicator() from try_pass")

            if page_arg_ctrl: page_arg_ctrl.update()

            if not self.can_put_area(self.turn):
                next_player_name = "白" if self.turn == 1 else "黒"
                print(f"{next_player_name}も置けません。両者ともパスとなり、ゲーム終了です。")
                self.end_game(page_arg_ctrl) 
            return True  
        
        return False 
    
    def end_game(self, page_arg_ctrl):
        white_count = np.sum(self.board == 1)
        black_count = np.sum(self.board == 2)
        
        print(f"DEBUG CONTROLLER: end_game called. White: {white_count}, Black: {black_count}. Page ID: {id(page_arg_ctrl)}")

        if hasattr(page_arg_ctrl, 'current_game_view_instance'):
            current_view_instance = page_arg_ctrl.current_game_view_instance
            if hasattr(current_view_instance, 'show_result_ui') and callable(getattr(current_view_instance, 'show_result_ui')):
                print(f"DEBUG CONTROLLER: Found callable current_game_view_instance.show_result_ui. Calling it.")
                current_view_instance.show_result_ui(white_count, black_count) 
            else:
                print(f"DEBUG CONTROLLER: current_game_view_instance.show_result_ui not found or not callable.")
        else:
            print(f"DEBUG CONTROLLER: page_arg_ctrl.current_game_view_instance not found.")
        
        print(f"ゲーム終了！ 白: {white_count}  黒: {black_count}") 
        if white_count > black_count: print("白の勝ち！")
        elif black_count > white_count: print("黒の勝ち！")
        else: print("引き分け！")