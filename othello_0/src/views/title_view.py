import flet as ft # type: ignore

class TitleView(ft.View):
  def __init__(self, page, route):
    

    super().__init__(
      route,
      [
        ft.Container(
          ft.Column(
            controls=[
              ft.Text("オセロ"),
              ft.ElevatedButton("Start", on_click=lambda _: page.go("/othello")),
            ],
          ),
          alignment=ft.alignment.center
        )
      ]
    )