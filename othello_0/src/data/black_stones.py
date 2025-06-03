import flet as ft # type: ignore



class BlackStones:
  def __init__(self):
    from settings import BOARD_SIZE
    self.black_stones = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]