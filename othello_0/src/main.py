import flet as ft # type: ignore

from views.title_view import TitleView
from views.game_view import GameView
from views.select_level_view import SelectLevelView
from views.select_turn_view import SelectTurnView

def main(page: ft.Page):
  page.window_full_screen = True
  page.window_maximized = True
  page.padding = 0
  page.title = "オセロ"
  page.level = "easy"
  page.player_color = "black"

  def route_change(e: ft.RouteChangeEvent):
    page.views.clear()
    if e.route == "/":
      page.views.append(
        TitleView(page, e.route)
      )
    elif e.route == "/select_level":
      page.views.append(
        SelectLevelView(page, e.route)
      )
    elif e.route == "/select_turn":
      page.views.append(
        SelectTurnView(page, e.route)
      )
    elif e.route == "/othello":
      page.views.append(
        GameView(page, e.route)
      )
    page.update()

  def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  page.go(page.route)


ft.app(main)