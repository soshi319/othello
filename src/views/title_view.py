import flet as ft # type: ignore
import settings

class TitleView(ft.View):
  def __init__(self, page, route):
    self.page = page
    
    w = page.width if page.width > 0 else 1280
    h = page.height if page.height > 0 else 720
    
    start_button_style = ft.ButtonStyle(
        bgcolor="#F05D23",
        color="#FFFFFF",
        overlay_color="#E02D2D",
        padding=20,
        shape=ft.RoundedRectangleBorder(radius=h * 0.05),
    )

    exit_button_style = ft.ButtonStyle(
        bgcolor="#4A5568",
        color="#FFFFFF",
        overlay_color="#2D3748",
        padding=5,
        shape=ft.RoundedRectangleBorder(radius=10),
    )
    
    def reset_settings(e):
        page.client_storage.clear()
        page.go("/init_settings")

    super().__init__(
      route,
      [
        ft.Stack(
           expand=True,
          controls=[
            ft.Image(
              src="/title.png",
              expand=True,
              fit=ft.ImageFit.COVER
            ),
            
            ft.Container(
              content=ft.ElevatedButton(
                # 文字サイズを画面幅の 1/30 に設定
                content=ft.Text("START", size=w // 30, weight=ft.FontWeight.BOLD),
                width=w * 0.25,   # 画面幅の 25%
                height=h * 0.15,  # 画面高さの 15%
                on_click=lambda _: page.go("/select_board_size") if settings.SELECT_BOARD else page.go("/select_level"),
                style=start_button_style,
              ),
              bottom=h * 0.25,    # 下から 25% の位置に配置
              left=0,
              right=0,
              alignment=ft.alignment.center
            ),

            # 右下：EXITボタン
            ft.Container(
              content=ft.ElevatedButton(
                content=ft.Text("EXIT", size=15, weight=ft.FontWeight.BOLD),
                width=100, 
                height=40,
                on_click=lambda _: page.window_close(),
                style=exit_button_style,
              ),
              right=20,
              bottom=20,
            ),

            # STARTボタンの下：記録ボタン
            ft.Container(
              content=ft.ElevatedButton(
                content=ft.Text("📊 記録", size=w // 60, weight=ft.FontWeight.BOLD),
                width=w * 0.15,
                height=h * 0.07,
                on_click=lambda _: page.go("/records"),
                style=exit_button_style,
              ),
              bottom=h * 0.15,
              left=0,
              right=0,
              alignment=ft.alignment.center,
            ),

            # 左下：設定初期化
            ft.Container(
              content=ft.TextButton(
                  "⚙️ 設定を初期化", 
                  on_click=reset_settings,
                  style=ft.ButtonStyle(color="#FFFFFF")
              ),
              left=20,
              bottom=20,
            ),
          ],
        )
      ],
      padding=0,
      bgcolor='#299643'
  )