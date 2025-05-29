import numpy as np
import random

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
        if can_put:
            row, col = random.choice(can_put)
            self.put_stone(row, col, page)
