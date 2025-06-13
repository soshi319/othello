import flet as ft  # type: ignore

class SelectTurnView(ft.View):
    def __init__(self, page, route):
        self.page = page

        style_black = ft.ButtonStyle(
            bgcolor="#222222", color="#FFFFFF", overlay_color="#888888",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )
        style_white = ft.ButtonStyle(
            bgcolor="#fafafa", color="#222222", overlay_color="#c1c1c1",
            padding=20, shape=ft.RoundedRectangleBorder(radius=10)
        )

        super().__init__(
            route,
            [
                ft.Stack(
                    controls=[
                        ft.Image(
                            src="/select_turn.png",
                            expand=True,
                            fit=ft.ImageFit.COVER
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        content=ft.Text("先攻（黒）でプレイ", size=36, weight=ft.FontWeight.BOLD),
                                        width=page.width * 0.4, height=page.width * 0.4,
                                        on_click=lambda _: (page.__setattr__("player_color", "black"), page.go("/othello")),
                                        opacity=0,
                                        style=style_black,
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("後攻（白）でプレイ", size=36, weight=ft.FontWeight.BOLD),
                                        width=page.width * 0.4, height=page.width * 0.4,
                                        on_click=lambda _: (page.__setattr__("player_color", "white"), page.go("/othello")),
                                        opacity=0,
                                        style=style_white,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=100,
                                expand=False,
                            ),
                            alignment=ft.alignment.center,
                            expand=True
                        ),
                    ],
                )
            ]
        )