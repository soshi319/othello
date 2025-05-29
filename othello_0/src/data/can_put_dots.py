import flet as ft # type: ignore

BOARD_SIZE = 6

class CanPutDots:
  can_put_dots = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]