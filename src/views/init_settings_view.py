import flet as ft # type: ignore
import settings
from data.records_manager import clear_records, clear_ai_records

class InitSettingsView(ft.View):
    def __init__(self, page, route):
        self.page = page

        # UIパーツの作成
        self.always_select_board_switch = ft.Switch(
            label="ゲーム開始時に毎回「盤面サイズ（6x6 / 8x8）」を選ぶ", 
            value=getattr(settings, 'SELECT_BOARD', True)
        )
        self.default_board_size_dropdown = ft.Dropdown(
            label="選ばない場合のデフォルト盤面サイズ",
            options=[ft.dropdown.Option("6"), ft.dropdown.Option("8")],
            value=str(getattr(settings, 'BOARD_SIZE', 6)),
            width=300
        )
        self.tf_wait_time = ft.TextField(label="AIの最低待機時間(秒)", value=str(getattr(settings, 'AI_WAIT_TIME', 0.8)), width=250)

        # 6x6用と8x8用の入力欄を生成する便利関数
        def create_ai_fields(size):
            return {
                "easy": ft.TextField(label="かんたん 探索回数", value=str(settings.AI_SIMULATIONS_EASY[size]), width=200),
                "hard": ft.TextField(label="むずかしい 探索回数", value=str(settings.AI_SIMULATIONS_HARD[size]), width=200),
                "master": ft.TextField(label="マスター 先読み深さ", value=str(settings.AI_DEPTH_MASTER[size]), width=200),
                "master_change": ft.TextField(label="マスター 終盤読み切り手数", value=str(settings.AI_CHANGE_TIME_MASTER[size]), width=200),
            }

        self.fields_6 = create_ai_fields(6)
        self.fields_8 = create_ai_fields(8)

        # タブの中身（レイアウト）を作る関数
        def create_tab_content(fields):
            return ft.Container(
                content=ft.Column([
                    ft.Row([fields["easy"], fields["hard"]]),
                    ft.Row([fields["master"], fields["master_change"]]),
                ], spacing=20),
                padding=20
            )

        # タブメニューの構築
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="6x6 盤面の設定", content=create_tab_content(self.fields_6)),
                ft.Tab(text="8x8 盤面の設定", content=create_tab_content(self.fields_8)),
            ],
            expand=1,
        )

        super().__init__(
            route,
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("初期 / 詳細セットアップ", size=40, weight=ft.FontWeight.BOLD),
                        
                        ft.Text("【全体・UIの設定】", size=20, weight=ft.FontWeight.BOLD),
                        self.always_select_board_switch,
                        self.default_board_size_dropdown,
                        self.tf_wait_time,
                        ft.Divider(),

                        ft.Text("【AIの強さ設定】", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(content=self.tabs, height=200),

                        ft.Divider(),

                        ft.Text("【データ管理】", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "対戦記録をすべてリセット（元に戻せません）",
                            on_click=self.reset_records,
                            style=ft.ButtonStyle(bgcolor="#E53E3E", color="#FFFFFF")
                        ),
                        ft.Divider(),

                        ft.ElevatedButton(
                            "設定を保存してスタート", 
                            on_click=self.save_and_start, 
                            style=ft.ButtonStyle(bgcolor="#4CAF50", color="#FFFFFF", padding=20)
                        )
                    ], spacing=20,
                    scroll=ft.ScrollMode.AUTO),
                    padding=40,
                    expand=True,
                )
            ]
        )

    def reset_records(self, e):
        clear_records()
        clear_ai_records()
        
        # 画面下に「リセットしました」という通知を数秒間表示する
        self.page.snack_bar = ft.SnackBar(ft.Text("対戦記録をリセットしました"))
        self.page.snack_bar.open = True
        self.page.update()

    def save_and_start(self, e):
        try:
            # 全体設定の保存
            settings.SELECT_BOARD = self.always_select_board_switch.value
            settings.BOARD_SIZE = int(self.default_board_size_dropdown.value)
            settings.AI_WAIT_TIME = float(self.tf_wait_time.value)

            self.page.client_storage.set("SELECT_BOARD", settings.SELECT_BOARD)
            self.page.client_storage.set("BOARD_SIZE", settings.BOARD_SIZE)
            self.page.client_storage.set("AI_WAIT_TIME", settings.AI_WAIT_TIME)

            # 6x6, 8x8 それぞれの値を読み取って辞書とストレージに保存
            for size, fields in [(6, self.fields_6), (8, self.fields_8)]:
                
                settings.AI_SIMULATIONS_EASY[size] = int(fields["easy"].value)
                settings.AI_SIMULATIONS_HARD[size] = int(fields["hard"].value)
                settings.AI_DEPTH_MASTER[size] = int(fields["master"].value)
                settings.AI_CHANGE_TIME_MASTER[size] = int(fields["master_change"].value)

                # PC内(ストレージ)に保存する際のキーは "AI_DEPTH_MASTER_6" のようにサイズを末尾につける
                self.page.client_storage.set(f"AI_SIMULATIONS_EASY_{size}", settings.AI_SIMULATIONS_EASY[size])
                self.page.client_storage.set(f"AI_SIMULATIONS_HARD_{size}", settings.AI_SIMULATIONS_HARD[size])
                self.page.client_storage.set(f"AI_DEPTH_MASTER_{size}", settings.AI_DEPTH_MASTER[size])
                self.page.client_storage.set(f"AI_CHANGE_TIME_MASTER_{size}", settings.AI_CHANGE_TIME_MASTER[size])

            self.page.client_storage.set("is_initialized", True)
            self.page.go("/")
            
        except ValueError:
            print("エラー: 設定値には正しい数値を入力してください。")
            pass