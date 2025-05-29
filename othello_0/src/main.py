import flet as ft # type: ignore

from views.title_view import TitleView
from views.game_view import GameView

def main(page: ft.Page):
  page.title = "三代目のオセロ"

  def route_change(e: ft.RouteChangeEvent):
    page.views.clear()
    if e.route == "/":
      page.views.append(
        TitleView(page, e.route)
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


ft.app(main, view=ft.AppView.WEB_BROWSER)