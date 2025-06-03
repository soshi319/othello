import flet as ft # type: ignore

class TitleView(ft.View):
  def __init__(self, page, route):
    self.page = page
    
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
              "START",
              width=page.width * 0.2,
              height=page.height * 0.15,
              on_click=lambda _: page.go("/select_level"),
              bottom=page.height * 0.25,
              style=ft.ButtonStyle(
                bgcolor="#F05D23",          # ボタンの背景色
                color="#FFFFFF",                # 文字色
                overlay_color="#E02D2D",    # 押下時の色
                padding=20,                           # テキストまわりの余白
                shape=ft.RoundedRectangleBorder(radius=page.height), # 丸み
                text_style=ft.TextStyle(size=40, weight=ft.FontWeight.BOLD), # フォントサイズや太さ
              ),
            ),
          ],
          alignment=ft.alignment.center,
        )
      ]
    )