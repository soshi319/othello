import os
import sys
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft # type: ignore

from settings import BOARD_SIZE

from controller.othello_controller import Othello
from data.white_stones import WhiteStones
from data.black_stones import BlackStones
from data.can_put_dots import CanPutDots
class GameView(ft.View):
    def __init__(self, page_arg, route):
        try:
            print(f"DEBUG GameView __init__: Received page_arg: {page_arg} (ID: {id(page_arg)})")
            
            self.page_ref = page_arg 
            page_arg.current_game_view_instance = self 

            self.white_stones = WhiteStones().white_stones
            self.black_stones = BlackStones().black_stones
            self.can_put_dots = CanPutDots().can_put_dots
            self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
            
            self.player_color = getattr(page_arg, "player_color", "black")
            self.ai_color = "white" if self.player_color == "black" else "black"

            ai_player_number_for_ctrl = 1 if self.ai_color == "white" else 2
            self.ai_player_number = ai_player_number_for_ctrl  # または適切な値
            
            self.start_button = ft.ElevatedButton(
                "START",
                on_click=self.on_click_start_game, # page_argを渡す必要がなくなりました
                style=ft.ButtonStyle( 
                    bgcolor="#FFFFFF", color="#000000", overlay_color="#818181",
                    padding=ft.padding.all(20), shape=ft.RoundedRectangleBorder(radius=10),
                    text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)
                ),
                height=70, width=250
            )
            
            self.result_text_control = ft.Text("結果計算中...", size=30, weight=ft.FontWeight.BOLD, color="#FFFFFF")
            self.result_score_control = ft.Text("白: 0  黒: 0", size=24, color="#FFFFFF")
            self.result_overlay = ft.Container(
                content=ft.Column(
                    [
                        self.result_text_control,
                        self.result_score_control,
                        ft.ElevatedButton(
                            "タイトルへ戻る",
                            on_click=self.go_to_title, # page_argを渡す必要がなくなりました
                            bgcolor="#4A5568", 
                            color="#FFFFFF",
                            width=200,
                            height=50,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center, expand=True,
                bgcolor="#80000000", # 黒の85%不透明
                visible=False, 
            )

            self.your_turn_image = ft.Image(
                src="/your_turn.png", # assetsフォルダ内のあなたのターン用画像
                width=400,            # 表示サイズは適宜調整
                height=120,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            )
            self.cpu_turn_image = ft.Image(
                src="/cpu_turn.png",   # assetsフォルダ内のCPUのターン用画像
                width=400,
                height=120,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            )

            self.turn_indicator_container = ft.Container(
                content=ft.Stack([self.your_turn_image, self.cpu_turn_image]),
                top=20,  # 画面上からの位置調整
                left=20, # 画面左からの位置調整
                padding=5,
                # bgcolor=ft.colors.with_opacity(0.5, ft.colors.BLUE_ACCENT) # デバッグ用背景色
            )

            othello_board_ui = self.makeOthelloBoard() # page_argを渡す必要がなくなりました
            
            self.start_button_container = ft.Container( 
                content=self.start_button,
                alignment=ft.alignment.center,
                expand=True
            )
            
            self.main_stack_controls = [
                othello_board_ui,
                self.turn_indicator_container, 
                self.start_button_container,
                self.result_overlay 
            ]
            
            super().__init__(
                route,
                [
                    ft.Stack(
                        controls=self.main_stack_controls,
                        expand=True
                    )
                ]
            )
        except Exception as e:
            with open("gameview_error.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
            # Optional: エラー内容をFlet画面上で表示したい場合
            super().__init__(
                route,
                [
                    ft.Text("GameViewの初期化中にエラーが発生しました"),
                    ft.Text(str(e)),
                ]
            )


    def update_turn_indicator(self):
        current_page = self.page_ref
        if not current_page: return

        player_turn_number_in_game_logic = 1 if self.player_color == "white" else 2
        
        is_player_turn = self.game.turn == player_turn_number_in_game_logic
        
        print(f"DEBUG VIEW: update_turn_indicator. Game turn: {self.game.turn}, Player color: {self.player_color}, Is Player Turn: {is_player_turn}")

        self.your_turn_image.visible = is_player_turn
        self.cpu_turn_image.visible = not is_player_turn
        
        # ゲーム終了時は両方非表示にする
        if self.result_overlay.visible: # 結果オーバーレイが表示されているか（ゲーム終了）で判断
             self.your_turn_image.visible = False
             self.cpu_turn_image.visible = False
        
        current_page.update() # ターン表示の変更をUIに反映


    def on_click_start_game(self, e):
        self.page_ref.update()   # ここでRef.currentが解決される

        # ここでRefを渡してコントローラ生成
        self.game = Othello(
            self.white_stones,   # 既にUIツリーに載っているRef
            self.black_stones,
            self.can_put_dots,
            self.ai_player_number  # 必要なパラメータ
        )

        self.game.start_game()
        self.game.update_can_put_dots_display()
        self.update_turn_indicator()
        if self.start_button_container in self.main_stack_controls:
            self.main_stack_controls.remove(self.start_button_container)
            if self.controls and isinstance(self.controls[0], ft.Stack):
                self.controls[0].controls = self.main_stack_controls
        self.page_ref.update()
        self.try_ai_move()


    def try_ai_move(self):
        current_page = self.page_ref
        ai_turn_in_controller = self.game.ai_player_number 
        
        print(f"DEBUG VIEW: try_ai_move. Game turn: {self.game.turn}, Controller AI Num: {ai_turn_in_controller}")

        if self.game.turn == ai_turn_in_controller:
            level = getattr(current_page, "level", "easy")
            print(f"DEBUG VIEW: AI's turn ({self.ai_color}). Level: {level}. Calling AI logic...")
            
            # AIの思考ルーチン呼び出し
            if level == "easy": self.game.ai_move(current_page)
            elif level == "normal": self.game.monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "hard": self.game.monte_carlo_ai_move(current_page, num_simulations=500)
            elif level == "master": self.game.alpha_beta_ai_move(current_page)
            
            print(f"DEBUG VIEW: AI logic call finished. Current game turn: {self.game.turn}")
            # AIが手を打った（またはパスした）後、コントローラ側でヒント更新とターン表示更新が行われる
            # GameView側でもターン表示を更新
            self.update_turn_indicator()
            # current_page.update() # page.updateはコントローラ内のput_stoneやtry_passで行われる
        else: # プレイヤーのターンになった場合
            print(f"DEBUG VIEW: Now Player's turn ({self.player_color}). Game turn: {self.game.turn}")
            self.update_turn_indicator() # プレイヤーのターン表示を確実にする
            # current_page.update() # コントローラ側で update されているはず

    def makeOthelloBoard(self):
        current_page = self.page_ref
        board_length = current_page.height * 0.8 
        grid_size = board_length / BOARD_SIZE
        container = ft.Container(height=current_page.height, width=current_page.width, bgcolor="#7decff")
        board_container = ft.Container(height=board_length + 1, width=board_length + 1, bgcolor="#8c00ff")
        board_green = ft.Container(height=board_length + 1, width=board_length + 1, bgcolor='#30AD30')
        board_shade = ft.Container(height=board_length, width=board_length, bgcolor='#404040', top=0, left=0)
        board_vertical_lines = [ft.Container(height=board_length, width=1, bgcolor='#000000', top=0, left=i * grid_size) for i in range(BOARD_SIZE + 1)]
        board_horizontal_lines = [ft.Container(height=1, width=board_length, bgcolor='#000000', top=i * grid_size, left=0) for i in range(BOARD_SIZE + 1)]
        dots = [ft.Container(height=5, width=5, bgcolor='#000000', top=i * grid_size - 2, left=j * grid_size - 2, border_radius=5) for i in [BOARD_SIZE//3, BOARD_SIZE*2//3] for j in [BOARD_SIZE//3, BOARD_SIZE*2//3]]
        white_disc_front = ft.Container(height=grid_size * 8 / 10, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#fafafa')
        white_disc_back = ft.Container(height=grid_size * 83 / 100, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#141212')
        white_discs = [ft.Stack(controls=[white_disc_back, white_disc_front], top=grid_size * row + grid_size * 1 / 10, left=grid_size * column + grid_size * 1 / 10, visible=False, ref=self.white_stones[row][column]) for row in range(BOARD_SIZE) for column in range(BOARD_SIZE)]
        black_disc_front = ft.Container(height=grid_size * 8 / 10, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#141212')
        black_disc_back = ft.Container(height=grid_size * 83 / 100, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#fafafa')
        black_discs = [ft.Stack(controls=[black_disc_back, black_disc_front], top=grid_size * row + grid_size * 1 / 10, left=grid_size * column + grid_size * 1 / 10, visible=False, ref=self.black_stones[row][column]) for row in range(BOARD_SIZE) for column in range(BOARD_SIZE)]
        click_areas_list = []
        for row_idx in range(BOARD_SIZE):
            for col_idx in range(BOARD_SIZE):
                btn = ft.CupertinoButton("T",
                    height=grid_size * 9 / 10, width=grid_size * 9 / 10, opacity=0,
                    top=grid_size * row_idx + grid_size * 1 / 20, left=grid_size * col_idx + grid_size * 1 / 20,
                    ref=self.click_areas[row_idx][col_idx],
                    on_click=lambda e, r=row_idx, c=col_idx: self.handle_player_move(r, c) 
                )
                click_areas_list.append(btn)
        can_put_dots_list = []
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                dot = ft.Container(height=grid_size * 2 / 10, width=grid_size * 2 / 10, bgcolor="#FFF671", border_radius=grid_size * 1 / 10, top=grid_size * row + grid_size * 4 / 10, left=grid_size * column + grid_size * 4 / 10, visible=False, ref=self.can_put_dots[row][column])
                can_put_dots_list.append(dot)
        othello = ft.Stack(controls=[board_container, board_shade, board_green, *board_vertical_lines, *board_horizontal_lines, *dots, *white_discs, *black_discs, *can_put_dots_list, *click_areas_list])
        stack = ft.Stack(controls=[container, othello], alignment=ft.alignment.center)
        return stack
    
    def handle_player_move(self, r, c):
        current_page = self.page_ref
        player_turn_in_controller = 1 if self.player_color == "white" else 2
        
        if self.game.turn == player_turn_in_controller:
            if (r,c) in self.game.can_put_area(self.game.turn):
                self.game.put_stone(r, c, current_page) # コントローラ内でヒントとページ更新
                self.update_turn_indicator() # プレイヤーの手の後にターン表示更新
                if self.game.turn != 0 :
                    self.try_ai_move() 

    def show_result_ui(self, white_count, black_count): 
        current_page_obj = self.page_ref 
        print(f"DEBUG VIEW: show_result_ui CALLED. White: {white_count}, Black: {black_count} on page {id(current_page_obj)}")
        score_text = f"あなた ({self.player_color}): {white_count if self.player_color == 'white' else black_count}  CPU ({self.ai_color}): {black_count if self.player_color == 'white' else white_count}"
        result_message = ""
        player_won = False; cpu_won = False
        if white_count > black_count: 
            if self.player_color == "white": player_won = True
            else: cpu_won = True
        elif black_count > white_count:
            if self.player_color == "black": player_won = True
            else: cpu_won = True
        if player_won: result_message = "あなたの勝ち！"
        elif cpu_won: result_message = "CPUの勝ち！"
        else: result_message = "引き分け！"
        
        self.result_text_control.value = result_message
        self.result_score_control.value = score_text
        self.result_overlay.visible = True 
        
        self.your_turn_image.visible = False # ゲーム終了時はターン表示を消す
        self.cpu_turn_image.visible = False
        
        print("DEBUG VIEW: Result overlay visible set to True. Updating page.")
        current_page_obj.update()

    def go_to_title(self, e): 
        current_page_obj = self.page_ref 
        print(f"DEBUG VIEW: go_to_title called on page {id(current_page_obj)}")
        self.result_overlay.visible = False 
        current_page_obj.update() 
        current_page_obj.go("/")