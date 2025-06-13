import flet as ft # type: ignore

import settings

class CanPutDots:
  def __init__(self):
    import settings
    self.can_put_dots = [[ft.Ref[ft.Stack]() for _ in range(settings.BOARD_SIZE)] for _ in range(settings.BOARD_SIZE)]