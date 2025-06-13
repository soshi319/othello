import flet as ft # type: ignore

import settings

class WhiteStones:
  def __init__(self):
    import settings
    self.white_stones = [[ft.Ref[ft.Stack]() for _ in range(settings.BOARD_SIZE)] for _ in range(settings.BOARD_SIZE)]