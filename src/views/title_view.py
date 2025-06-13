import flet as ft # type: ignore

class TitleView(ft.View):
  def __init__(self, page, route):
    self.page = page
    
    start_button_style = ft.ButtonStyle(
        bgcolor="#F05D23",
        color="#FFFFFF",
        overlay_color="#E02D2D",
        padding=20,
        shape=ft.RoundedRectangleBorder(radius=page.height),
    )
    
    super().__init__(
      route,
      [
        ft.Stack(
          controls=[
            ft.Image(
              src="/title.png",
              expand=True,
              fit=ft.ImageFit.COVER
            ),
            ft.ElevatedButton(
              content=ft.Text("START", size=40, weight=ft.FontWeight.BOLD),
              width=page.width * 0.2,
              height=page.height * 0.15,
              on_click=lambda _: page.go("/select_board_size"),
              bottom=page.height * 0.25,
              style=start_button_style,
            ),
          ],
        )
      ],
      vertical_alignment=ft.MainAxisAlignment.CENTER,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )