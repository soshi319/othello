import flet as ft
from data.records_manager import load_records, load_ai_records

# 画像のパスを削除し、(ラベル名, 色) のシンプルな構成に変更
DIFFICULTY_LABELS = {
    "easy":   ("かんたん",   "#81d9eb"),
    "normal": ("ふつう",     "#fae465"),
    "hard":   ("むずかしい", "#fca14b"),
    "master": ("マスター",   "#f7a0c0"),
}

class RecordsView(ft.View):
    def __init__(self, page, route):
        self.page = page
        self.w = page.width if page.width > 0 else 1280
        self.h = page.height if page.height > 0 else 720

        self.is_ai_mode = False

        # 初期データの読み込みと表の作成
        records = load_records()
        rows = self._build_rows(records, self.h)

        self.records_column = ft.Column(
            controls=rows,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # 切り替えボタン
        self.mode_segmented_button = ft.SegmentedButton(
            allow_multiple_selection=False,
            selected={"player"},
            on_change=self._on_mode_change,
            segments=[
                ft.Segment(value="player", label=ft.Text("👤 プレイヤー vs AI", weight=ft.FontWeight.BOLD)),
                ft.Segment(value="ai", label=ft.Text("🤖 AI vs AI", weight=ft.FontWeight.BOLD)),
            ],
        )

        super().__init__(
            route,
            [
                ft.Container(
                    expand=True,
                    bgcolor="#1a4a1a",
                    content=ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            controls=[
                                ft.Text("対戦記録", size=48, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ft.Container(height=10),
                                
                                self.mode_segmented_button,
                                ft.Container(height=15),

                                ft.Container(
                                    content=self.records_column,
                                    bgcolor="#CC111111",
                                    border_radius=16,
                                    padding=30,
                                    width=self.w * 0.55,
                                ),
                                ft.Container(height=20),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            "タイトルへ戻る",
                                            on_click=lambda _: page.go("/"),
                                            style=ft.ButtonStyle(
                                                bgcolor="#F05D23",
                                                color="#FFFFFF",
                                                padding=14,
                                                shape=ft.RoundedRectangleBorder(radius=8)
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),
                    ),
                )
            ],
            padding=0,
            bgcolor='#299643'
        )

    def _on_mode_change(self, e):
        """タブが切り替わったときの処理"""
        selected_set = e.control.selected
        self.is_ai_mode = "ai" in selected_set
        
        if self.is_ai_mode:
            records = load_ai_records()
            rows = self._build_ai_matrix_rows(records, self.h)
        else:
            records = load_records()
            rows = self._build_rows(records, self.h)

        self.records_column.controls = rows
        self.page.update()

    def _build_rows(self, records, h):
        """プレイヤー vs AI 用の通常の行を作る"""
        rows = []
        rows.append(
            ft.Row(
                controls=[
                    ft.Container(width=200, content=ft.Text("難易度", size=18, color="#AAAAAA", weight=ft.FontWeight.BOLD)),
                    ft.Container(width=80,  content=ft.Text("勝ち",   size=18, color="#FFD700", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                    ft.Container(width=80,  content=ft.Text("負け",   size=18, color="#FF6666", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                    ft.Container(width=80,  content=ft.Text("引分",   size=18, color="#AAAAAA", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                    ft.Container(width=80,  content=ft.Text("合計",   size=18, color="#FFFFFF", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                    ft.Container(width=90,  content=ft.Text("勝率",   size=18, color="#88FFAA", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                ],
                spacing=0,
            )
        )
        rows.append(ft.Divider(color="#444444"))

        for diff, (label, color) in DIFFICULTY_LABELS.items():
            rec = records.get(diff, {"win": 0, "lose": 0, "draw": 0})
            win, lose, draw = rec["win"], rec["lose"], rec["draw"]
            total = win + lose + draw
            rate  = f"{win / total * 100:.1f}%" if total > 0 else "-"

            rows.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=200,
                            content=ft.Text(label, size=18, color=color, weight=ft.FontWeight.BOLD),
                            padding=ft.padding.only(left=10),
                        ),
                        ft.Container(width=80, content=ft.Text(str(win),   size=22, color="#FFD700", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                        ft.Container(width=80, content=ft.Text(str(lose),  size=22, color="#FF6666", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                        ft.Container(width=80, content=ft.Text(str(draw),  size=22, color="#AAAAAA", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                        ft.Container(width=80, content=ft.Text(str(total), size=22, color="#FFFFFF",  weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                        ft.Container(width=90, content=ft.Text(rate,       size=22, color="#88FFAA", weight=ft.FontWeight.BOLD), alignment=ft.alignment.center),
                    ],
                    spacing=0,
                )
            )
        return rows

    def _get_gradient_color(self, rate):
        """勝率(0〜100)に応じて、赤(#FF6666) -> 白(#FFFFFF) -> 金(#FFD700) のグラデーションカラーを生成する"""
        if rate < 50:
            # 0%〜50%: 赤(255, 102, 102) から 白(255, 255, 255) へ変化
            t = rate / 50.0
            r = 255
            g = int(102 + t * (255 - 102))
            b = int(102 + t * (255 - 102))
        else:
            # 50%〜100%: 白(255, 255, 255) から 金(255, 215, 0) へ変化
            t = (rate - 50.0) / 50.0
            r = 255
            g = int(255 + t * (215 - 255))
            b = int(255 + t * (0 - 255))
            
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build_ai_matrix_rows(self, records, h):
        """AI vs AI 用の総当たり表（マトリックス）を作る"""
        rows = []
        
        rows.append(
            ft.Text("※ 各AI同士の合算戦績です（斜めの同キャラ対決のみ先攻の勝敗）", size=14, color="#AAAAAA")
        )

        table = ft.Column(spacing=0)
        diff_keys = list(DIFFICULTY_LABELS.keys())

        header_row = ft.Row(spacing=0, alignment=ft.MainAxisAlignment.CENTER)
        header_row.controls.append(
            ft.Container(
                width=130, height=45,
                border=ft.border.all(1, "#555555"),
                bgcolor="#222222",
                content=ft.Text(" 基準 \\ 相手", size=14, color="#AAAAAA"),
                alignment=ft.alignment.center
            )
        )
        for w_diff in diff_keys:
            label = DIFFICULTY_LABELS[w_diff][0]
            header_row.controls.append(
                ft.Container(
                    width=100, height=45,
                    border=ft.border.all(1, "#555555"),
                    bgcolor="#222222",
                    content=ft.Text(label, size=15, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center
                )
            )
        table.controls.append(header_row)

        for b_diff in diff_keys:
            b_label, b_color = DIFFICULTY_LABELS[b_diff]
            row = ft.Row(spacing=0, alignment=ft.MainAxisAlignment.CENTER)
            
            row.controls.append(
                ft.Container(
                    width=130, height=65,
                    border=ft.border.all(1, "#555555"),
                    bgcolor="#222222",
                    content=ft.Text(b_label, size=14, color=b_color, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center
                )
            )

            for w_diff in diff_keys:
                rec = records.get(b_diff, {}).get(w_diff, {"win": 0, "lose": 0, "draw": 0})
                w, l, d = rec["win"], rec["lose"], rec["draw"]
                total = w + l + d

                bg = "#2a2a2a" if b_diff == w_diff else None 

                if total == 0:
                    content = ft.Text("-", size=18, color="#555555")
                else:
                    rate = w / total * 100
                    text = f"{w}勝 {l}敗"
                    if d > 0: 
                        text += f" {d}分"
                    
                    full_text = f"{text}\n({rate:.1f}%)"
                    
                    # 勝率に応じたグラデーションカラーを取得
                    dynamic_color = self._get_gradient_color(rate)
                    
                    content = ft.Text(full_text, size=13, color=dynamic_color, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

                row.controls.append(
                    ft.Container(
                        width=100, height=65,
                        border=ft.border.all(1, "#555555"),
                        bgcolor=bg,
                        content=content,
                        alignment=ft.alignment.center
                    )
                )
            table.controls.append(row)

        rows.append(table)
        return rows