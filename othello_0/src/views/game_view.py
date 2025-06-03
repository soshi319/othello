# game_view.py (ファイル21の修正案)
import os
import sys
import flet as ft # type: ignore
import time

BOARD_SIZE = 6

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.controller.othello_controller import Othello
from src.data.white_stones import WhiteStones
from src.data.black_stones import BlackStones
from src.data.can_put_dots import CanPutDots

class GameView(ft.View):
    def __init__(self, page_arg, route):
        print(f"DEBUG GameView __init__: Received page_arg: {page_arg} (ID: {id(page_arg)})")
        
        self.page_ref = page_arg # オリジナルのpageオブジェクトを保持

        # ★★★ GameViewのインスタンスをpageオブジェクトのカスタム属性に保存 ★★★
        page_arg.current_game_view_instance = self 
        print(f"DEBUG GameView __init__: Set page_arg.current_game_view_instance to self (ID: {id(self)})")

        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        self.player_color = getattr(page_arg, "player_color", "black")
        self.ai_color = "white" if self.player_color == "black" else "black"

        ai_player_number_for_ctrl = 1 if self.ai_color == "white" else 2
        self.game = Othello(ai_player_number=ai_player_number_for_ctrl) 

        self.start_button = ft.ElevatedButton(
            "START",
            on_click=self.on_click_start_game, # page_argを渡す必要がなくなる可能性
            style=ft.ButtonStyle( 
                bgcolor="#FFFFFF", color="#000000", overlay_color="#818181",
                padding=ft.padding.all(20), shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)
            ),
            height=70, width=250
        )
        
        self.result_text_control = ft.Text("結果計算中...", size=30, weight=ft.FontWeight.BOLD, color="#FFFFFF") # 文字色を白に
        self.result_score_control = ft.Text("白: 0  黒: 0", size=24, color="#FFFFFF") # 文字色を白に
        self.result_overlay = ft.Container(
            content=ft.Column(
                [
                    self.result_text_control,
                    self.result_score_control,
                    ft.ElevatedButton(
                        "タイトルへ戻る",
                        on_click=self.go_to_title, 
                        # bgcolor="#444444", # 例: グレー系の背景色
                        # color="#FFFFFF",   # 例: 白色の文字
                        width=200,
                        height=50,
                        style=ft.ButtonStyle(
                            bgcolor="#4A5568", # 例: 少し青みがかったグレー
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
            # ★★★ bgcolorを直接指定 ★★★
            bgcolor="#D9000000", # 黒の85%不透明
            visible=False, 
        )
        
        othello_board_ui = self.makeOthelloBoard() # page_argを渡す必要がなくなる可能性
        
        self.start_button_container = ft.Container( 
            content=self.start_button,
            alignment=ft.alignment.center,
            expand=True
        )
        
        self.main_stack_controls = [
            othello_board_ui,
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

    def on_click_start_game(self, e): # current_page引数を削除
        current_page = self.page_ref # self.page_ref を使用
        print(f"DEBUG VIEW: on_click_start_game called on page {id(current_page)}")
        self.game.start_game() 
        self.game.update_can_put_dots_display()
        
        if self.start_button_container in self.main_stack_controls:
            self.main_stack_controls.remove(self.start_button_container)
            if self.controls and isinstance(self.controls[0], ft.Stack):
                self.controls[0].controls = self.main_stack_controls
        
        current_page.update()
        self.try_ai_move() # current_page引数を削除


    def try_ai_move(self): # current_page引数を削除
        current_page = self.page_ref # self.page_ref を使用
        ai_turn_in_controller = self.game.ai_player_number 
        
        print(f"DEBUG VIEW: try_ai_move. Game turn: {self.game.turn}, Controller AI Num: {ai_turn_in_controller}")

        if self.game.turn == ai_turn_in_controller:
            level = getattr(current_page, "level", "easy")
            print(f"DEBUG VIEW: AI's turn ({self.ai_color}). Level: {level}. Calling AI logic...") # メッセージ変更
            
            # ★★★ AIの思考ルーチン呼び出しのコメントアウトを解除 ★★★
            if level == "easy":
                self.game.ai_move(current_page)
            elif level == "normal":
                self.game.monte_carlo_ai_move(current_page, num_simulations=100) # シミュレーション回数は適宜調整
            elif level == "hard":
                self.game.monte_carlo_ai_move(current_page, num_simulations=500)
            elif level == "master":
                self.game.monte_carlo_ai_move(current_page, num_simulations=1000)
            
            print(f"DEBUG VIEW: AI logic call finished. Current game turn: {self.game.turn}") # AI処理後のターン確認
            # AIが手を打った（またはパスした）後、ターンがプレイヤーに変わっていれば、
            # OthelloController側のput_stoneやtry_passでヒント更新とpage.updateが行われるはず。
            # 必要であれば、ここで再度ヒント更新とpage.updateを検討。
            # ただし、通常はコントローラ側で完結させるのが望ましい。
            # if self.game.turn != ai_turn_in_controller: # ターンが変わっていたら (プレイヤーのターンになったら)
            #    self.game.update_can_put_dots_display()
            #    current_page.update()

        # else:
            # print("DEBUG VIEW: Not AI's turn in try_ai_move.")

    def makeOthelloBoard(self): # current_page引数を削除
        current_page = self.page_ref # self.page_ref を使用
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
                    on_click=lambda e, r=row_idx, c=col_idx: self.handle_player_move(r, c) # current_page引数を削除
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
    
    def handle_player_move(self, r, c): # current_page引数を削除
        current_page = self.page_ref # self.page_ref を使用
        player_turn_in_controller = 1 if self.player_color == "white" else 2
        
        if self.game.turn == player_turn_in_controller:
            if (r,c) in self.game.can_put_area(self.game.turn):
                self.game.put_stone(r, c, current_page)
                if self.game.turn != 0 :
                    self.try_ai_move() # current_page引数を削除

    # ★★★ show_result_ui の引数から current_page_obj を削除 ★★★
    def show_result_ui(self, white_count, black_count): 
        current_page_obj = self.page_ref 
        print(f"DEBUG VIEW: show_result_ui CALLED. White: {white_count}, Black: {black_count} on page {id(current_page_obj)}")
        
        score_text = f"あなた ({self.player_color}): {white_count if self.player_color == 'white' else black_count}  CPU ({self.ai_color}): {black_count if self.player_color == 'white' else white_count}"
        
        result_message = ""
        player_won = False
        cpu_won = False

        if white_count > black_count: # 白の石が多い
            if self.player_color == "white":
                player_won = True
            else: # プレイヤーは黒
                cpu_won = True
        elif black_count > white_count: # 黒の石が多い
            if self.player_color == "black":
                player_won = True
            else: # プレイヤーは白
                cpu_won = True
        # else: 引き分けの場合はどちらも False のまま

        if player_won:
            result_message = "あなたの勝ち！"
        elif cpu_won:
            result_message = "CPUの勝ち！"
        else:
            result_message = "引き分け！"
        
        self.result_text_control.value = result_message
        self.result_score_control.value = score_text # スコア表示も更新
        self.result_overlay.visible = True 
        
        print("DEBUG VIEW: Result overlay visible set to True. Updating page.")
        current_page_obj.update()
        
    def go_to_title(self, e): 
        current_page_obj = self.page_ref 
        print(f"DEBUG VIEW: go_to_title called on page {id(current_page_obj)}")
        self.result_overlay.visible = False 
        current_page_obj.update() 
        current_page_obj.go("/")