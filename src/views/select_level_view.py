import flet as ft  # type: ignore

class SelectLevelView(ft.View):
    def __init__(self, page, route):
        self.page = page

        # ボタンのスタイル定義（これは変更なし）
        style_master = ft.ButtonStyle(
            bgcolor="#f7a0c0", color="#FFFFFF", overlay_color="#e6578b",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )
        style_hard = ft.ButtonStyle(
            bgcolor="#fca14b", color="#FFFFFF", overlay_color="#f08f34",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )
        style_normal = ft.ButtonStyle(
            bgcolor="#fae465", color="#FFFFFF", overlay_color="#f7d337",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )
        style_easy = ft.ButtonStyle(
            bgcolor="#81d9eb", color="#FFFFFF", overlay_color="#41baee",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )
        style_oni = ft.ButtonStyle(
            bgcolor="#000000", color="#999999", overlay_color="#d80000",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )

        super().__init__(
            route,
            [
                ft.Stack(
                    controls=[
                        # --- レイヤー1：背景 ---
                        # expand=TrueでStack全体に広がる背景画像
                        ft.Image(
                            src="/select_level.png",
                            expand=True,
                            fit=ft.ImageFit.COVER
                        ),

                        # --- レイヤー2：中央揃えのコンテンツ ---
                        # このContainerもexpand=TrueでStack全体に広がる
                        ft.Container(
                            # この中のColumnが中央に配置される
                            content=ft.Column(
                                controls=[
                                    ft.ElevatedButton(
                                        content=ft.Text("マスター", size=page.width // 30, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: (page.__setattr__("level", "master"), page.go("/select_turn")),
                                        width=page.width // 6, height=page.height // 7, style=style_master,
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("むずかしい", size=page.width // 30, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: (page.__setattr__("level", "hard"), page.go("/select_turn")),
                                        width=page.width // 6, height=page.height // 7, style=style_hard,
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("ふつう", size=page.width // 30, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: (page.__setattr__("level", "normal"), page.go("/select_turn")),
                                        width=page.width // 6, height=page.height // 7, style=style_normal,
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("かんたん", size=page.width // 30, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: (page.__setattr__("level", "easy"), page.go("/select_turn")),
                                        width=page.width // 6, height=page.height // 7, style=style_easy,
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("鬼", size=10, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: (page.__setattr__("level", "oni"), page.go("/select_turn")),
                                        width=10, height=10, style=style_oni,
                                    ),
                                ],
                                # Column自体の内部での配置設定
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=30,
                            ),
                            # Containerの機能で、content(Column)を中央に配置
                            alignment=ft.alignment.center,
                            top=page.height * 0.15,
                            left=0,
                            right=0,
                            expand=True,
                        ),
                    ]
                )
            ]
        )