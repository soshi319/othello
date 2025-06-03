import os
import sys
import flet as ft # type: ignore

BOARD_SIZE = 6

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.controller.othello_controller import Othello
from src.data.white_stones import WhiteStones
from src.data.black_stones import BlackStones
from src.data.can_put_dots import CanPutDots

# game_view.py

# ... (import文など) ...

class GameView(ft.View):
    def __init__(self, page_arg, route): # 引数名を page から page_arg に変更して区別しやすくする
        print(f"DEBUG GameView __init__: Received page_arg: {page_arg} (ID: {id(page_arg)})")
        
        self.page_ref = page_arg # インスタンス変数に保持するが、super() の影響を受ける可能性を考慮
                                # 主に他のメソッドで使うために保持するが、コールバック登録には page_arg を直接使う

        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # self.page = page_arg # ここで代入しても super() で None になる可能性がある

        self.player_color = getattr(page_arg, "player_color", "black")
        self.ai_color = "white" if self.player_color == "black" else "black"

        # Othelloインスタンスの初期化 (使用するコントローラに合わせてください)
        self.game = Othello() 
        # ai_player_number = 1 if self.ai_color == "white" else 2
        # self.game = Othello(ai_player_number=ai_player_number)


        self.start_button = ft.ElevatedButton(
            "START",
            on_click=lambda e: self.on_click_start_game(e, page_arg) # page_arg を渡す
            # ... (styleなどはそのまま) ...
        )
        
        self.result_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ゲーム結果"),
            content=ft.Text("ここに結果が表示されます。"), 
            actions=[
                ft.TextButton("タイトルへ戻る", on_click=lambda e: self.go_to_title(e, page_arg)), # page_arg を渡す
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        othello_board_ui = self.makeOthelloBoard(page_arg) # page_arg を渡す
        
        self.main_stack_controls = [
            othello_board_ui,
            ft.Container( 
                content=self.start_button,
                alignment=ft.alignment.center,
                expand=True
            )
        ]

        # ★★★ コールバックの登録を super().__init__ の「前」に行い、引数の page_arg を使用 ★★★
        # page_arg が None でないことを確認
        if page_arg is not None:
            page_arg.show_game_result_callback = lambda wc, bc: self.show_result_dialog(wc, bc, page_arg) # page_arg を渡す
            print(f"DEBUG VIEW: Callback 'show_game_result_callback' registered ON page_arg (ID: {id(page_arg)}) BEFORE super().__init__")
        else:
            print("DEBUG VIEW: ERROR - page_arg is None BEFORE super().__init__ and callback registration.")

        super().__init__(
            route,
            [
                ft.Stack(
                    controls=self.main_stack_controls,
                    expand=True
                )
            ]
        )
        page_arg.show_game_result_callback = lambda wc, bc: self.show_result_dialog(wc, bc, page_arg)


    def on_click_start_game(self, e, current_page): # current_page を受け取る
        print(f"DEBUG VIEW: on_click_start_game called on page {id(current_page)}")
        self.game.start_game()
        
        if hasattr(self.game, 'update_can_put_dots_display'):
             self.game.update_can_put_dots_display()
        elif hasattr(self.game, 'can_put_area_visible'): 
            if self.player_color == "black" and self.game.turn == 2:
                self.game.can_put_area_visible()
            elif self.player_color == "white": 
                if hasattr(self.game, 'can_put_area_unvisible'):
                    self.game.can_put_area_unvisible()
        
        button_container_to_remove = None
        for ctrl in self.main_stack_controls:
            if isinstance(ctrl, ft.Container) and ctrl.content == self.start_button:
                button_container_to_remove = ctrl
                break
        if button_container_to_remove:
            self.main_stack_controls.remove(button_container_to_remove)
            if self.controls and isinstance(self.controls[0], ft.Stack):
                self.controls[0].controls = self.main_stack_controls
        
        current_page.update() # current_page を使用
        self.try_ai_move(current_page) # current_page を渡す

    def try_ai_move(self, current_page): # current_page を受け取る
        ai_turn_number = 1 if self.ai_color == "white" else 2
        if self.game.turn == ai_turn_number:
            level = getattr(current_page, "level", "easy") # current_page を使用
            if level == "easy":
                self.game.ai_move(current_page) # current_page を使用
            # ... (他のAIレベルも同様に current_page を渡す) ...
            elif level == "normal":
                self.game.monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "hard":
                self.game.monte_carlo_ai_move(current_page, num_simulations=500)
            elif level == "master":
                self.game.monte_carlo_ai_move(current_page, num_simulations=1000)


    def makeOthelloBoard(self, current_page): # current_page を受け取る
        # ... (このメソッド内で page の代わりに current_page を使用) ...
        board_length = current_page.height * 0.8 
        # ...
        # on_click=lambda e, r=row_idx, c=col_idx: self.handle_player_move(r, c, current_page)
        # ...
        # (以下、同様に page を current_page に置き換える)
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
                    on_click=lambda e, r=row_idx, c=col_idx: self.handle_player_move(r, c, current_page) # current_page を渡す
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
    
    def handle_player_move(self, r, c, current_page): # current_page を受け取る
        player_turn_number = 1 if self.player_color == "white" else 2
        if self.game.turn == player_turn_number:
            if (r,c) in self.game.can_put_area(self.game.turn):
                self.game.put_stone(r, c, current_page) # current_page を使用
                if self.game.turn != 0 :
                    self.try_ai_move(current_page) # current_page を使用

    def show_result_dialog(self, white_count, black_count, current_page):
        result_text = f"白: {white_count}  黒: {black_count}\n\n"
        if white_count > black_count:
            result_text += "白の勝ち！"
        elif black_count > white_count:
            result_text += "黒の勝ち！"
        else:
            result_text += "引き分け！"
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("ゲーム結果"),
            content=ft.Text(result_text, text_align=ft.TextAlign.CENTER, size=18),
            actions=[ft.TextButton("タイトルへ戻る", on_click=lambda e: current_page.go("/"))],
        )
        current_page.dialog = dlg
        dlg.open = True
        current_page.update()

    def go_to_title(self, e, current_page): # current_page を受け取る
        print("DEBUG VIEW: go_to_title called")
        if current_page.dialog:  # current_page を使用
            current_page.dialog.open = False
        current_page.go("/") # current_page を使用