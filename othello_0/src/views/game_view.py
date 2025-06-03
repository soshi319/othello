# game_view.py (ファイル27の修正案)
import os
import sys
import flet as ft # type: ignore

BOARD_SIZE = 6

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.controller.othello_controller import Othello # ファイル26のOthelloControllerを参照
from src.data.white_stones import WhiteStones
from src.data.black_stones import BlackStones
from src.data.can_put_dots import CanPutDots

class GameView(ft.View):
    def __init__(self, page_arg, route):
        print(f"DEBUG GameView __init__: Received page_arg: {page_arg} (ID: {id(page_arg)})")
        
        self.page_ref = page_arg 

        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        self.player_color = getattr(page_arg, "player_color", "black")
        self.ai_color = "white" if self.player_color == "black" else "black"

        # ★★★ AIのプレイヤー番号を決定し、Othelloインスタンスに渡す ★★★
        ai_player_number_for_ctrl = 1 if self.ai_color == "white" else 2
        self.game = Othello(ai_player_number=ai_player_number_for_ctrl) 


        self.start_button = ft.ElevatedButton(
            "START",
            on_click=lambda e: self.on_click_start_game(e, page_arg),
            style=ft.ButtonStyle( 
                bgcolor="#FFFFFF", color="#000000", overlay_color="#818181",
                padding=ft.padding.all(20), shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)
            ),
            height=70, width=250
        )
        
        self.result_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ゲーム結果"),
            content=ft.Text("ここに結果が表示されます。"), 
            actions=[
                ft.TextButton("タイトルへ戻る", on_click=lambda e: self.go_to_title(e, page_arg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        othello_board_ui = self.makeOthelloBoard(page_arg)
        
        self.main_stack_controls = [
            othello_board_ui,
            ft.Container( 
                content=self.start_button,
                alignment=ft.alignment.center,
                expand=True
            )
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
        # pageへのコールバック登録は不要 (コントローラから直接ビューのメソッドを呼ぶため)


    def on_click_start_game(self, e, current_page):
        print(f"DEBUG VIEW: on_click_start_game called on page {id(current_page)}")
        self.game.start_game() # この中で初期配置が行われる
        
        # ★★★ ゲーム開始時のヒント表示を update_can_put_dots_display に統一 ★★★
        self.game.update_can_put_dots_display()
        
        button_container_to_remove = None
        for ctrl in self.main_stack_controls:
            if isinstance(ctrl, ft.Container) and ctrl.content == self.start_button:
                button_container_to_remove = ctrl
                break
        if button_container_to_remove:
            self.main_stack_controls.remove(button_container_to_remove)
            if self.controls and isinstance(self.controls[0], ft.Stack):
                self.controls[0].controls = self.main_stack_controls
        
        current_page.update()
        self.try_ai_move(current_page)

    def try_ai_move(self, current_page):
        # OthelloController側でai_player_numberを使って判定するので、
        # ここでは単純に現在のターンがAIの論理的な手番と一致するかを見るだけでよい。
        # AIがどちらの色かは self.ai_color で判定。
        ai_turn_in_controller = self.game.ai_player_number # コントローラ内のAIの手番
        
        print(f"DEBUG VIEW: try_ai_move. Game turn: {self.game.turn}, Controller AI Num: {ai_turn_in_controller}")

        if self.game.turn == ai_turn_in_controller: # 現在のゲームのターンが、コントローラが認識するAIのターンか
            level = getattr(current_page, "level", "easy")
            print(f"DEBUG VIEW: AI's turn ({self.ai_color}). Level: {level}")
            if level == "easy":
                self.game.ai_move(current_page)
            elif level == "normal":
                self.game.monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "hard":
                self.game.monte_carlo_ai_move(current_page, num_simulations=500)
            elif level == "master":
                self.game.monte_carlo_ai_move(current_page, num_simulations=1000)
        # else:
            # print(f"DEBUG VIEW: Not AI's turn. Player ({self.player_color}) should move.")


    def makeOthelloBoard(self, current_page):
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
                    on_click=lambda e, r=row_idx, c=col_idx: self.handle_player_move(r, c, current_page) 
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
    
    def handle_player_move(self, r, c, current_page):
        player_turn_in_controller = 1 if self.player_color == "white" else 2
        
        if self.game.turn == player_turn_in_controller:
            if (r,c) in self.game.can_put_area(self.game.turn):
                self.game.put_stone(r, c, current_page)
                if self.game.turn != 0 :
                    self.try_ai_move(current_page)

    def show_result_dialog(self, white_count, black_count, current_page_obj):
        print(f"DEBUG VIEW: show_result_dialog CALLED. White: {white_count}, Black: {black_count} on page {id(current_page_obj)}")
        result_text = f"白: {white_count}  黒: {black_count}\n\n"
        if white_count > black_count: result_text += "白の勝ち！"
        elif black_count > white_count: result_text += "黒の勝ち！"
        else: result_text += "引き分け！"
        
        self.result_dialog.content = ft.Text(result_text, text_align=ft.TextAlign.CENTER, size=18)
        
        current_page_obj.dialog = self.result_dialog
        self.result_dialog.open = True
        
        print("DEBUG VIEW: Dialog open set to True. Updating page.")
        current_page_obj.update()

    def go_to_title(self, e, current_page_obj):
        print("DEBUG VIEW: go_to_title called")
        if current_page_obj.dialog: 
            current_page_obj.dialog.open = False
        current_page_obj.go("/")