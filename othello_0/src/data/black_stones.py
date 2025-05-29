import flet as ft # type: ignore

BOARD_SIZE = 6

class BlackStones:
  black_stones = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]