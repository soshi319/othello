import flet as ft  # type: ignore

class SelectLevelView(ft.View):
    def __init__(self, page, route):
        self.page = page

        super().__init__(
            route,
            [
                ft.Stack(
                    controls=[
                        ft.Image(
                            src="/select_level.png",
                            expand=True,
                            fit=ft.ImageFit.COVER
                        ),
                        ft.Column(
                            controls=[
                                ft.ElevatedButton(
                                    "マスター",
                                    on_click=lambda _: (page.__setattr__("level", "master"), page.go("/select_turn")),
                                    width=300, height=130,
                                    style=ft.ButtonStyle(
                                        bgcolor="#f7a0c0",
                                        color="#FFFFFF",
                                        overlay_color="#e6578b",  # 赤系濃い色
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        text_style=ft.TextStyle(size=40, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "むずかしい",
                                    on_click=lambda _: (page.__setattr__("level", "hard"), page.go("/select_turn")),
                                    width=300, height=130,
                                    style=ft.ButtonStyle(
                                        bgcolor="#fca14b",
                                        color="#FFFFFF",
                                        overlay_color="#f08f34",  # 橙系濃い色
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        text_style=ft.TextStyle(size=40, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "ふつう",
                                    on_click=lambda _: (page.__setattr__("level", "normal"), page.go("/select_turn")),
                                    width=300, height=130,
                                    style=ft.ButtonStyle(
                                        bgcolor="#fae465",
                                        color="#FFFFFF",
                                        overlay_color="#f7d337",  # 緑系濃い色
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        text_style=ft.TextStyle(size=40, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "かんたん",
                                    on_click=lambda _: (page.__setattr__("level", "easy"), page.go("/select_turn")),
                                    width=300, height=130,
                                    style=ft.ButtonStyle(
                                        bgcolor="#81d9eb",
                                        color="#FFFFFF",
                                        overlay_color="#41baee",  # ← 濃い水色（hover時）
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        text_style=ft.TextStyle(size=40, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "鬼",
                                    on_click=lambda _: (page.__setattr__("level", "oni"), page.go("/select_turn")),
                                    width=10, height=10,
                                    style=ft.ButtonStyle(
                                        bgcolor="#000000",
                                        color="#999999",
                                        overlay_color="#d80000",  # ← 濃い水色（hover時）
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        text_style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=30,
                            expand=False,
                        ),
                    ],
                    alignment=ft.alignment.center,
                )
            ]
        )
