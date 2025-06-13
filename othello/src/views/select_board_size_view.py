import flet as ft  # type: ignore

# 動的に BOARD_SIZE を切り替えるため、settings モジュールの
# グローバル変数を直接上書きします。
import settings


class SelectBoardSizeView(ft.View):
    """6×6 / 8×8 どちらの盤面サイズで遊ぶかを選択するビュー。

    盤面サイズを決定したら settings.BOARD_SIZE を書き換え、
    次の難易度選択画面へ遷移します。
    """

    def __init__(self, page: ft.Page, route: str):
        self.page = page

        super().__init__(
            route,
            [
                ft.Stack(
                    controls=[
                        # ★ 好みで差し替えられる背景画像を設定（任意）
                        ft.Image(
                            src="/select_board_size.png",  # 用意できなければ削除して OK
                            expand=True,
                            fit=ft.ImageFit.COVER,
                        ),
                        ft.Column(
                            controls=[
                                ft.ElevatedButton(
                                    "６ × ６ でプレイ",
                                    on_click=lambda _: self._select_size(6),
                                    width=320,
                                    height=140,
                                    style=ft.ButtonStyle(
                                        bgcolor="#4CAF50",             # グリーン
                                        color="#FFFFFF",
                                        overlay_color="#3e8e41",       # 押下時の濃い色
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        text_style=ft.TextStyle(size=42, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "８ × ８ でプレイ",
                                    on_click=lambda _: self._select_size(8),
                                    width=320,
                                    height=140,
                                    style=ft.ButtonStyle(
                                        bgcolor="#2196F3",             # ブルー
                                        color="#FFFFFF",
                                        overlay_color="#0b7dda",
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        text_style=ft.TextStyle(size=42, weight=ft.FontWeight.BOLD),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=40,
                        ),
                    ],
                    alignment=ft.alignment.center,
                ),
            ],
        )

    # ---------------------------------------------------------------------
    # internal helpers
    # ---------------------------------------------------------------------
    def _select_size(self, size: int) -> None:
        """盤面サイズを確定し、settings.BOARD_SIZE を更新して次の画面へ。"""

        # 1. settings のグローバル変数を書き換え
        settings.BOARD_SIZE = size

        # 2. ページにも覚えさせておくと、他ビューで参照しやすい
        self.page.__setattr__("board_size", size)

        # 3. 難易度選択画面へ遷移
        self.page.go("/select_level")
