import flet as ft # type: ignore

BOARD_SIZE = 6

class WhiteStones:
  white_stones = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]