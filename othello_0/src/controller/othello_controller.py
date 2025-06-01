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
        # 中心4マスに初期配置
        c = BOARD_SIZE // 2
        self.board[c-1, c-1] = 1
        self.board[c, c] = 1
        self.board[c-1, c] = 2
        self.board[c, c-1] = 2

        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots

        # 白：１　黒：２
        self.turn = 2

    def start_game(self):
        c = BOARD_SIZE // 2
        self.flip([(c-1, c-1), (c, c)], 1)
        self.flip([(c-1, c), (c, c-1)], 2)
        self.can_put_area_visible()
  
    def put_stone(self, row, column, page):
        if not self.can_put_area(self.turn):
            if self.try_pass(page):
                page.update()
                return
        if (row, column) in self.can_put_area(self.turn):
            if self.turn == 1:
                self.flip(self.flip_area(row, column), 1)
                self.turn = 2
                self.can_put_area_visible()
            elif self.turn == 2:
                self.flip(self.flip_area(row, column), 2)
                self.turn = 1
                self.can_put_area_visible()
            page.update()
  
    def can_put_area_visible(self):
        can_flip_area = self.can_put_area(self.turn)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.can_put_dots[i][j].current.visible = False

        for row, column in can_flip_area:
            self.can_put_dots[row][column].current.visible = True

    def can_put_area(self, turn):
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        flip_list = []

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                can_flip = False

                # 白番
                if turn == 1 and self.board[i, j] not in (1, 2):
                    for direction_column, direction_row in directions:
                        row = i + direction_row
                        column = j + direction_column
                        temporary_can_flip = False

                        while 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 2:
                            row += direction_row
                            column += direction_column
                            temporary_can_flip = True
                        if temporary_can_flip and 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 1:
                            can_flip = True

                # 黒番
                elif turn == 2 and self.board[i, j] not in (1, 2):
                    for direction_column, direction_row in directions:
                        row = i + direction_row
                        column = j + direction_column
                        temporary_can_flip = False

                        while 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 1:
                            row += direction_row
                            column += direction_column
                            temporary_can_flip = True
                        if temporary_can_flip and 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 2:
                            can_flip = True

                if can_flip:
                    flip_list.append((i, j))
        
        return flip_list

    def flip_area(self, row, column):
        turn = self.turn
        i = row
        j = column
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        flip_list = []

        can_flip = False

        # 白番
        if turn == 1:
            for direction_column, direction_row in directions:
                row = i + direction_row
                column = j + direction_column
                temporary_flip_list = []
                temporary_can_flip = False

                while 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 2:
                    temporary_flip_list.append((row, column))
                    row += direction_row
                    column += direction_column
                    temporary_can_flip = True
                if temporary_can_flip and 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 1:
                    can_flip = True
                    flip_list.extend(temporary_flip_list)

        # 黒番
        elif turn == 2:
            for direction_column, direction_row in directions:
                row = i + direction_row
                column = j + direction_column
                temporary_flip_list = []
                temporary_can_flip = False

                while 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 1:
                    temporary_flip_list.append((row, column))
                    row += direction_row
                    column += direction_column
                    temporary_can_flip = True
                if temporary_can_flip and 0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE and self.board[row, column] == 2:
                    can_flip = True
                    flip_list.extend(temporary_flip_list)
      
        if can_flip:
            flip_list.append((i, j))
        
        return flip_list

    def flip(self, flip_list, sign):
        for row, column in flip_list:
            self.board[row, column] = sign
            if sign == 1:
                self.white_stones[row][column].current.visible = True
                self.black_stones[row][column].current.visible = False
            elif sign == 2:
                self.white_stones[row][column].current.visible = False
                self.black_stones[row][column].current.visible = True

    def ai_move(self, page):
        can_put = self.can_put_area(self.turn)
        if not can_put:
            if self.try_pass(page):
                page.update()
                return
        if can_put:
            time.sleep(0.5)
            row, col = random.choice(can_put)
            self.put_stone(row, col, page)
    
    def monte_carlo_ai_move(self, page, num_simulations=500):
        can_put = self.can_put_area(self.turn)
        if not can_put:
            if self.try_pass(page):
                page.update()
                return
            
        best_winrate = -1
        best_move = None
        for row, col in can_put:
            win = 0
            for _ in range(num_simulations):
                winner = self.simulate_game_from_move(row, col)
                if winner == self.turn:
                    win += 1
            winrate = win / num_simulations
            print(f"手 ({row},{col}) の勝率: {winrate:.2f}")
            if winrate > best_winrate:
                best_winrate = winrate
                best_move = (row, col)

        if best_move is not None:
            time.sleep(0.2)  # 演出用
            self.put_stone(best_move[0], best_move[1], page)
            print("モンテカルロ発動！")

    def simulate_game_from_move(self, row, col):
        sim_board = np.copy(self.board)
        sim_turn = self.turn

        # 最初の一手を打つ
        self._simulate_put_stone(sim_board, row, col, sim_turn)
        sim_turn = 3 - sim_turn

        # 盤面が埋まるまで繰り返し
        while np.any(sim_board == 0):
            can_put = self._simulate_can_put_area(sim_board, sim_turn)
            if not can_put:
                sim_turn = 3 - sim_turn
                # もし両方打てなければbreak（最終盤面で両方置けない場合対策）
                if not self._simulate_can_put_area(sim_board, sim_turn):
                    break
                continue
            move = random.choice(can_put)
            self._simulate_put_stone(sim_board, move[0], move[1], sim_turn)
            sim_turn = 3 - sim_turn

        white_count = np.sum(sim_board == 1)
        black_count = np.sum(sim_board == 2)
        if white_count > black_count:
            return 1
        elif black_count > white_count:
            return 2
        else:
            return 0
        
    def _simulate_put_stone(self, board, row, col, turn):
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        flip_list = []
        for direction_column, direction_row in directions:
            r = row + direction_row
            c = col + direction_column
            temp_flip = []
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r, c] == (3 - turn):
                temp_flip.append((r, c))
                r += direction_row
                c += direction_column
            if temp_flip and 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r, c] == turn:
                flip_list.extend(temp_flip)
        flip_list.append((row, col))
        for r, c in flip_list:
            board[r, c] = turn

    def _simulate_can_put_area(self, board, turn):
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        flip_list = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i, j] in (1, 2):
                    continue
                can_flip = False
                for direction_column, direction_row in directions:
                    row = i + direction_row
                    col = j + direction_column
                    found = False
                    while 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row, col] == (3 - turn):
                        row += direction_row
                        col += direction_column
                        found = True
                    if found and 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row, col] == turn:
                        can_flip = True
                if can_flip:
                    flip_list.append((i, j))
        return flip_list
    
    def try_pass(self, page):
        legal_moves = self.can_put_area(self.turn)
        if not legal_moves:
            print("パスします")  # ページ上にメッセージを出したい
            self.turn = 3 - self.turn  # 1⇔2を切り替え
            self.can_put_area_visible()
            if not self.can_put_area(self.turn):
                print("両者とも置けません。ゲーム終了")
                self.end_game(page)
            return True  # パスした
        return False  # パスしなかった
    
    def end_game(self, page):
        white_count = np.sum(self.board == 1)
        black_count = np.sum(self.board == 2)
        print(f"白: {white_count}  黒: {black_count}")

        if white_count > black_count:
            print("白の勝ち！")
        elif white_count < black_count:
            print("黒の勝ち！")
        else:
            print("引き分け！")
