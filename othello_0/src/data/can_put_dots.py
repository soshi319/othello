import flet as ft # type: ignore

from settings import BOARD_SIZE

class CanPutDots:
  def __init__(self):
    from settings import BOARD_SIZE
    self.can_put_dots = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]