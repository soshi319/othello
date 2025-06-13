import flet as ft  # type: ignore

import settings

class SelectBoardSizeView(ft.View):
    def __init__(self, page: ft.Page, route: str):
        self.page = page

        # ボタンのスタイル定義（変更なし）
        style_6x6 = ft.ButtonStyle(
            bgcolor="#4CAF50",
            color="#FFFFFF",
            overlay_color="#3e8e41",
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        style_8x8 = ft.ButtonStyle(
            bgcolor="#2196F3",
            color="#FFFFFF",
            overlay_color="#0b7dda",
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        super().__init__(
            route,
            [
                ft.Stack(
                    controls=[
                        # レイヤー1：背景
                        ft.Image(
                            src="/select_board_size.png",
                            expand=True,
                            fit=ft.ImageFit.COVER,
                        ),
                        # レイヤー2：中央揃えのコンテンツ
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ElevatedButton(
                                        content=ft.Text("６ × ６ でプレイ", size=42, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: self._select_size(6),
                                        width=320,
                                        height=140,
                                        style=style_6x6,
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("８ × ８ でプレイ", size=42, weight=ft.FontWeight.BOLD),
                                        on_click=lambda _: self._select_size(8),
                                        width=320,
                                        height=140,
                                        style=style_8x8,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=40,
                            ),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    ],
                ),
            ],
        )

    def _select_size(self, size: int) -> None:
        settings.BOARD_SIZE = size
        self.page.__setattr__("board_size", size)
        self.page.go("/select_level")