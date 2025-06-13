import flet as ft # type: ignore



class BlackStones:
  def __init__(self):
    import settings
    self.black_stones = [[ft.Ref[ft.Stack]() for _ in range(settings.BOARD_SIZE)] for _ in range(settings.BOARD_SIZE)]