# othello_controller.py (BOARD_SIZE=8 対応・numpy未使用版)
import random
import time

import settings

from data.black_stones import BlackStones
from data.white_stones import WhiteStones
from data.can_put_dots import CanPutDots

class Othello:
    # --- (変更点 1) 8x8盤用の評価テーブルをリストで定義 ---
    # 位置評価用の 6×6 重み表
    _WEIGHTS_6x6 = [
        [100, -20,  10,  10, -20, 100],
        [-20, -50,  -2,  -2, -50, -20],
        [ 10,  -2,   5,   5,  -2,  10],
        [ 10,  -2,   5,   5,  -2,  10],
        [-20, -50,  -2,  -2, -50, -20],
        [100, -20,  10,  10, -20, 100],
    ]
    # 位置評価用の 8×8 重み表 (標準的なもの)
    _WEIGHTS_8x8 = [
        [120, -20,  20,   5,   5,  20, -20, 120],
        [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
        [ 20,  -5,  15,   3,   3,  15,  -5,  20],
        [  5,  -5,   3,   3,   3,   3,  -5,   5],
        [  5,  -5,   3,   3,   3,   3,  -5,   5],
        [ 20,  -5,  15,   3,   3,  15,  -5,  20],
        [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
        [120, -20,  20,   5,   5,  20, -20, 120],
    ]
    # -------------------------------------------

    def __init__(self, white_stones, black_stones, can_put_dots, ai_player_number=None):
        import settings
        self.board = [[0] * settings.BOARD_SIZE for _ in range(settings.BOARD_SIZE)]
        c = settings.BOARD_SIZE // 2
        self.board[c-1][c-1] = 1; self.board[c][c] = 1
        self.board[c-1][c] = 2; self.board[c][c-1] = 2
        # 外から受け取ったRefで管理
        self.white_stones = white_stones
        self.black_stones = black_stones
        self.can_put_dots = can_put_dots
        self.turn = 2
        self.ai_player_number = ai_player_number
        self.ai_move_count = 0
        
        # --- (変更点 2) BOARD_SIZE に応じて評価テーブルを選択 ---
        if settings.BOARD_SIZE == 8:
            self.weights = self._WEIGHTS_8x8
        elif settings.BOARD_SIZE == 6:
            self.weights = self._WEIGHTS_6x6
        else:
            # サポート外のサイズでは位置評価を無効化 (ゼロ行列)
            self.weights = [[0] * settings.BOARD_SIZE for _ in range(settings.BOARD_SIZE)]
        # ----------------------------------------------------

        print(f"DEBUG CONTROLLER __init__: Turn: {self.turn}, AI Player Num: {self.ai_player_number}")

    def start_game(self):
        print("DEBUG CONTROLLER: start_game called")
        c = settings.BOARD_SIZE // 2
        self.flip([(c-1, c-1), (c, c)], 1)
        self.flip([(c-1, c), (c, c-1)], 2)
        # ヒント表示は GameView の on_click_start_game 内で update_can_put_dots_display を呼び出す

    def update_can_put_dots_display(self):
        for i in range(settings.BOARD_SIZE):
            for j in range(settings.BOARD_SIZE):
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
        for r_idx in range(settings.BOARD_SIZE):
            for c_idx in range(settings.BOARD_SIZE):
                if self.board[r_idx][c_idx] == 0: 
                    can_place_here = False
                    opponent_color = 3 - turn_to_check
                    for dr, dc in directions:
                        stones_in_between = []
                        curr_r, curr_c = r_idx + dr, c_idx + dc
                        while 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and self.board[curr_r][curr_c] == opponent_color:
                            stones_in_between.append((curr_r, curr_c))
                            curr_r += dr
                            curr_c += dc
                        if stones_in_between and 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and self.board[curr_r][curr_c] == turn_to_check:
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
            while 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and self.board[curr_r][curr_c] == opponent_color:
                current_line_flips.append((curr_r, curr_c))
                curr_r += dr
                curr_c += dc
            if current_line_flips and 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and self.board[curr_r][curr_c] == turn_making_move:
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
            self.board[row][column] = sign
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
    
    def upgraded_monte_carlo_ai_move(self, page, num_simulations=50):
        """
        Monte-Carlo 法で着手を選ぶ。
        ただし AI の着手数が 5 手未満の間は X マス
          (例: 6x6盤なら (1,1),(1,4),(4,1),(4,4)) を候補から除外する。
        """
        possible_moves = self.can_put_area(self.turn)
        if not possible_moves:
            if self.try_pass(page):
                return
            return
        
        if self.ai_move_count < 5:
            x_squares = {(1, 1), (1, settings.BOARD_SIZE-2),
                         (settings.BOARD_SIZE-2, 1), (settings.BOARD_SIZE-2, settings.BOARD_SIZE-2)}
            filtered = [mv for mv in possible_moves if mv not in x_squares]
            if filtered:
                possible_moves = filtered

        best_winrate, best_move = -1, None
        for r, c in possible_moves:
            win = 0
            for _ in range(num_simulations):
                if self.simulate_game_from_move(r, c) == self.turn:
                    win += 1
            winrate = win / num_simulations
            if winrate > best_winrate:
                best_winrate, best_move = winrate, (r, c)

        if best_move is None:
            best_move = random.choice(possible_moves)

        self.put_stone(best_move[0], best_move[1], page)

        if self.ai_player_number == self.turn:
            pass
        else:
            self.ai_move_count += 1

    
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
            self.put_stone(best_move[0], best_move[1], page)
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
        sim_board = [row[:] for row in self.board] # numpy.copy -> list copy
        current_sim_turn = self.turn 
        self._simulate_put_stone(sim_board, r_sim, c_sim, current_sim_turn)
        current_sim_turn = 3 - current_sim_turn 
        passes_in_a_row = 0
        while any(0 in row for row in sim_board) and passes_in_a_row < 2: # np.any
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
        white_count = sum(row.count(1) for row in sim_board) # np.sum
        black_count = sum(row.count(2) for row in sim_board) # np.sum
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
        board_s[r_s][c_s] = turn_s
        for dr_s, dc_s in directions:
            stones_to_flip_in_line = []
            curr_r, curr_c = r_s + dr_s, c_s + dc_s
            while 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and board_s[curr_r][curr_c] == opponent_s:
                stones_to_flip_in_line.append((curr_r, curr_c))
                curr_r += dr_s
                curr_c += dc_s
            if stones_to_flip_in_line and 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and board_s[curr_r][curr_c] == turn_s:
                for r_f, c_f in stones_to_flip_in_line:
                    board_s[r_f][c_f] = turn_s

    def _simulate_can_put_area(self, board_s, turn_s):
        opponent_s = 3 - turn_s
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        possible_moves_s = []
        for r_idx_s in range(settings.BOARD_SIZE):
            for c_idx_s in range(settings.BOARD_SIZE):
                if board_s[r_idx_s][c_idx_s] == 0:
                    can_place_here_s = False
                    for dr_s, dc_s in directions:
                        stones_in_between_s = []
                        curr_r, curr_c = r_idx_s + dr_s, c_idx_s + dc_s
                        while 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and board_s[curr_r][curr_c] == opponent_s:
                            stones_in_between_s.append((curr_r, curr_c))
                            curr_r += dr_s
                            curr_c += dc_s
                        if stones_in_between_s and 0 <= curr_r < settings.BOARD_SIZE and 0 <= curr_c < settings.BOARD_SIZE and board_s[curr_r][curr_c] == turn_s:
                            can_place_here_s = True
                            break
                    if can_place_here_s:
                        possible_moves_s.append((r_idx_s, c_idx_s))
        return possible_moves_s
    
    # ============================================================

    # --- (変更点 3) 静的評価関数を self.weights を使うように修正 (numpy未使用) ---
    def _evaluate_static(self, board_sta, turn_sta):
        """
        位置重み + モビリティ差の評価値を返す。
        インスタンスの self.weights を使用して評価する。
        """
        opp = 3 - turn_sta

        # --- 位置重み (初期化時に選択された self.weights を使用) ---
        my_score = 0
        opp_score = 0
        for r in range(settings.BOARD_SIZE):
            for c in range(settings.BOARD_SIZE):
                if board_sta[r][c] == turn_sta:
                    my_score += self.weights[r][c]
                elif board_sta[r][c] == opp:
                    opp_score += self.weights[r][c]
        pos_score = my_score - opp_score

        # --- モビリティ（合法手数差）----------------------------------
        mob_score = 2 * (
            len(self._simulate_can_put_area(board_sta, turn_sta)) -
            len(self._simulate_can_put_area(board_sta, opp))
        )

        return pos_score + mob_score
    # --------------------------------------------------------

    def _clone_after_move_static(self, board_sta, r_sta, c_sta, turn_sta):
        """board_sta をコピーし (r,c) へ turn_sta が打った盤面を返す."""
        new_brd = [row[:] for row in board_sta] # numpy.copy -> list copy
        self._simulate_put_stone(new_brd, r_sta, c_sta, turn_sta)
        return new_brd

    def _negamax(self, board_ng, turn_ng, depth, alpha, beta):
        """Negamax 本体。評価値を返す."""
        moves = self._simulate_can_put_area(board_ng, turn_ng)
        if depth == 0 or not moves:
            if not moves and self._simulate_can_put_area(board_ng, 3 - turn_ng):
                return -self._negamax(board_ng, 3 - turn_ng,
                                      depth, -beta, -alpha)
            return self._evaluate_static(board_ng, turn_ng)

        best = -1e9
        for r, c in moves:
            child = self._clone_after_move_static(board_ng, r, c, turn_ng)
            val = -self._negamax(child, 3 - turn_ng,
                                 depth - 1, -beta, -alpha)
            best = max(best, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return best

    def alpha_beta_ai_move(self, page, depth=5):
        """
        深さ `depth` の α–β 探索で最善手を指す。
        """
        possible_moves = self.can_put_area(self.turn)
        if not possible_moves:
            if self.try_pass(page):
                return
            return

        best_val = -1e9
        best_move = None
        for r, c in sorted(possible_moves,
                           key=lambda rc: -len(self._simulate_can_put_area(
                               self._clone_after_move_static(
                                   self.board, rc[0], rc[1], self.turn),
                               3 - self.turn))):
            next_board = self._clone_after_move_static(self.board, r, c, self.turn)
            val = -self._negamax(next_board, 3 - self.turn,
                                 depth - 1, -1e9, 1e9)
            if val > best_val:
                best_val = val
                best_move = (r, c)

        if best_move is not None:
            self.put_stone(best_move[0], best_move[1], page)
            
    #---------------------------------------------------------------------------------
    def _disc_diff(self, board_td, turn_td):
        my  = sum(row.count(turn_td) for row in board_td) # np.sum
        opp = sum(row.count(3 - turn_td) for row in board_td) # np.sum
        return my - opp

    # --- (変更点 4) 終盤探索の評価値の初期値を BOARD_SIZE に応じて変更 ---
    def _negamax_terminal(self, board_nt, turn_nt,
                          passes=0, alpha=None, beta=None):
        # 盤面サイズに合わせた評価値の最大/最小値
        max_score = settings.BOARD_SIZE * settings.BOARD_SIZE
        if alpha is None:
            alpha = -max_score - 1
        if beta is None:
            beta = max_score + 1

        moves = self._simulate_can_put_area(board_nt, turn_nt)

        if not moves:
            if passes == 1:
                return self._disc_diff(board_nt, turn_nt)
            return -self._negamax_terminal(board_nt, 3 - turn_nt,
                                           passes + 1, -beta, -alpha)

        best = -max_score - 1 # あり得る最小スコアより小さい値
        for r, c in moves:
            child = self._clone_after_move_static(board_nt, r, c, turn_nt)
            val = -self._negamax_terminal(child, 3 - turn_nt,
                                           0, -beta, -alpha)
            best = max(best, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return best

    def endgame_negamax_ai_move(self, page):
        possible = self.can_put_area(self.turn)
        if not possible:
            self.try_pass(page)
            return

        max_score = settings.BOARD_SIZE * settings.BOARD_SIZE
        best_val, best_move = -max_score - 1, None # あり得る最小スコアより小さい値
        for r, c in possible:
            child = self._clone_after_move_static(self.board, r, c, self.turn)
            # 初回呼び出しでは alpha/beta を渡さず、_negamax_terminal 内部で設定させる
            val = -self._negamax_terminal(child, 3 - self.turn)
            if val > best_val:
                best_val, best_move = val, (r, c)
        
        if best_move:
            self.put_stone(best_move[0], best_move[1], page)

        if self.ai_player_number is not None and self.turn != self.ai_player_number:
            self.ai_move_count += 1
    # -------------------------------------------------------------------

    def hybrid_ai_move(self, page, depth=7, switch_ai_moves=11):
        """
        AI が switch_ai_moves (既定11) 手を打つまでは α–β 探索、
        12 手目以降は終局まで Negamax。
        """
        if self.ai_move_count <= switch_ai_moves:
            self.alpha_beta_ai_move(page, depth)
        else:
            self.endgame_negamax_ai_move(page)

    
    #---------------------------------------------------------------------------------

    
    def try_pass(self, page_arg_ctrl):
        current_turn_before_pass = self.turn
        print(f"DEBUG CONTROLLER: try_pass called for turn {current_turn_before_pass}")
        
        if not self.can_put_area(current_turn_before_pass): 
            current_player_name = "白" if current_turn_before_pass == 1 else "黒"
            print(f"{current_player_name}の番: 置ける場所がないためパスします。")
            
            self.turn = 3 - current_turn_before_pass  
            print(f"DEBUG CONTROLLER: Turn changed to {self.turn} after {current_player_name}'s pass.")
            
            self.update_can_put_dots_display() 
            
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
            else:
                if self.ai_player_number is not None and self.turn == self.ai_player_number:
                    if hasattr(page_arg_ctrl, "current_game_view_instance"):
                        gv = page_arg_ctrl.current_game_view_instance
                        if hasattr(gv, "try_ai_move") and callable(gv.try_ai_move):
                            print("DEBUG CONTROLLER: try_pass -> calling GameView.try_ai_move()")
                            gv.try_ai_move()

            return True
        return False 
    
    def end_game(self, page_arg_ctrl):
        white_count = sum(row.count(1) for row in self.board) # np.sum
        black_count = sum(row.count(2) for row in self.board) # np.sum
        
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