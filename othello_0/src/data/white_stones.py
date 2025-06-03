import flet as ft # type: ignore

from settings import BOARD_SIZE

class WhiteStones:
  def __init__(self):
    from settings import BOARD_SIZE
    self.white_stones = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]