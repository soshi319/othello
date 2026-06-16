import flet as ft
import settings

class SelectAiView(ft.View):
    def __init__(self, page, route):
        self.page = page

        # 難易度ごとのデザイン・配色定義
        self.colors = {
            "master": {"bg": "#20f7a0c0", "act": "#f7a0c0", "name": "マスター"},
            "hard":   {"bg": "#20fca14b", "act": "#fca14b", "name": "むずかしい"},
            "normal": {"bg": "#20fae465", "act": "#fae465", "name": "ふつう"},
            "easy":   {"bg": "#2081d9eb", "act": "#81d9eb", "name": "かんたん"},
            "oni":    {"bg": "#20000000", "act": "#000000", "name": "鬼"},
        }

        # ラベルテキストの用意
        self.black_status_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF")
        self.white_status_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF")

        # ボタンを配置するColumn
        self.black_buttons = ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.white_buttons = ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.update_ui_state()

        super().__init__(
            route,
            [
                ft.Container(
                    expand=True,
                    image_src="/select_level.png",
                    image_fit=ft.ImageFit.COVER,
                    # 修正箇所: ft.Alignment ではなく ft.Container を使用し、alignment に設定する
                    content=ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            controls=[
                                ft.Text("AI vs AI 観戦設定", size=36, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ft.Container(height=10),
                                ft.Row(
                                    controls=[
                                        # 先攻（黒）カラム
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text("先攻 (黒)", size=18, color="#CCCCCC", weight=ft.FontWeight.W_500),
                                                self.black_status_text,
                                                ft.Container(height=5),
                                                self.black_buttons
                                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=25, bgcolor="#CC111111", border_radius=15, width=240
                                        ),
                                        ft.Text("VS", size=45, weight=ft.FontWeight.BOLD, color="#FFD700"),
                                        # 後攻（白）カラム
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text("後攻 (白)", size=18, color="#CCCCCC", weight=ft.FontWeight.W_500),
                                                self.white_status_text,
                                                ft.Container(height=5),
                                                self.white_buttons
                                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=25, bgcolor="#CC111111", border_radius=15, width=240
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=40
                                ),
                                ft.Container(height=25),
                                # 観戦スタートボタン
                                ft.ElevatedButton(
                                    content=ft.Text("観戦スタート", size=22, weight=ft.FontWeight.BOLD),
                                    on_click=self.start_spectating,
                                    style=ft.ButtonStyle(
                                        bgcolor="#FFD700", color="#000000", overlay_color="#D4AF37",
                                        padding=20, shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    width=240, height=60
                                ),
                                ft.TextButton("戻る", on_click=lambda _: page.go("/select_level"), style=ft.ButtonStyle(color="#FFFFFF"))
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15
                        )
                    )
                )
            ],
            padding=0,
            bgcolor='#299643'
        )

    def update_ui_state(self):
        """選択状態に合わせてテキストとアクティブボタンのスタイルを再構築する"""
        self.black_status_text.value = self.colors[self.page.ai_black_level]["name"]
        self.white_status_text.value = self.colors[self.page.ai_white_level]["name"]

        self.black_buttons.controls.clear()
        self.white_buttons.controls.clear()

        levels = ["master", "hard", "normal", "easy", "oni"]
        for lvl in levels:
            # 先攻（黒）のボタン生成
            is_b_active = (self.page.ai_black_level == lvl)
            b_style = ft.ButtonStyle(
                bgcolor=self.colors[lvl]["act"] if is_b_active else self.colors[lvl]["bg"],
                color="#FFFFFF" if (is_b_active or lvl == "oni") else "#222222",
                padding=12, shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(3, "#FFFFFF") if is_b_active else None
            )
            b_text = ft.Text("鬼" if lvl == "oni" else self.colors[lvl]["name"], size=16, weight=ft.FontWeight.BOLD)
            if lvl == "oni" and not is_b_active: b_text.color = "#888888"

            self.black_buttons.controls.append(
                ft.ElevatedButton(content=b_text, style=b_style, width=180, on_click=lambda _, l=lvl: self.select_level("black", l))
            )

            # 後攻（白）のボタン生成
            is_w_active = (self.page.ai_white_level == lvl)
            w_style = ft.ButtonStyle(
                bgcolor=self.colors[lvl]["act"] if is_w_active else self.colors[lvl]["bg"],
                color="#FFFFFF" if (is_w_active or lvl == "oni") else "#222222",
                padding=12, shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(3, "#FFFFFF") if is_w_active else None
            )
            w_text = ft.Text("鬼" if lvl == "oni" else self.colors[lvl]["name"], size=16, weight=ft.FontWeight.BOLD)
            if lvl == "oni" and not is_w_active: w_text.color = "#888888"

            self.white_buttons.controls.append(
                ft.ElevatedButton(content=w_text, style=w_style, width=180, on_click=lambda _, l=lvl: self.select_level("white", l))
            )

    def select_level(self, turn, level):
        if turn == "black":
            self.page.ai_black_level = level
        else:
            self.page.ai_white_level = level
        self.update_ui_state()
        self.page.update()

    def start_spectating(self, e):
        self.page.is_ai_vs_ai = True  # 観戦モードを明示的にセット
        self.page.go("/othello")