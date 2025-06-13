import os
import sys
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft # type: ignore

import settings
# ▼ 難易度／手番ごとのアイコン（assets フォルダに置く）
DIFFICULTY_ICONS = {
    "easy":   "/level_easy.png",
    "normal": "/level_normal.png",
    "hard":   "/level_hard.png",
    "master": "/level_master.png",
    "oni":    "/level_oni.png",
}

TURN_ICONS = {
    "black": "/turn_black.png",   # 先手（黒）
    "white": "/turn_white.png",   # 後手（白）
}


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
            self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(settings.BOARD_SIZE)] for _ in range(settings.BOARD_SIZE)]
            
            self.player_color = getattr(page_arg, "player_color", "black")
            self.ai_color = "white" if self.player_color == "black" else "black"
            
            self.level = getattr(page_arg, "level", "easy")

            ai_player_number_for_ctrl = 1 if self.ai_color == "white" else 2
            self.ai_player_number = ai_player_number_for_ctrl
            
            self.button_style1 = ft.ButtonStyle( 
                    bgcolor="#FFFFFF", color="#000000", overlay_color="#818181",
                    padding=ft.padding.all(20), shape=ft.RoundedRectangleBorder(radius=10)
                )
            
            self.start_button = ft.ElevatedButton(
                content=ft.Text("START", size=24, weight=ft.FontWeight.BOLD),
                on_click=self.on_click_start_game,
                style=self.button_style1,
                height=70, width=250
            )
            
            self.result_text_control = ft.Text("結果計算中...", size=30, weight=ft.FontWeight.BOLD, color="#FFFFFF")
            self.result_score_control = ft.Text("白: 0  黒: 0", size=24, color="#FFFFFF")
            self.result_difficulty_icon = ft.Image(
                src=DIFFICULTY_ICONS.get(self.level, DIFFICULTY_ICONS["easy"]),
                width=200, height=60, fit=ft.ImageFit.CONTAIN
            )
            self.result_turn_icon = ft.Image(
                src=TURN_ICONS.get(self.player_color, TURN_ICONS["black"]),
                width=60, height=60, fit=ft.ImageFit.CONTAIN
            )
            
            self.result_overlay = ft.Container(
                content=ft.Column(
                    [
                        self.result_text_control,
                        self.result_score_control,
                        ft.Row(
                            controls=[self.result_difficulty_icon, self.result_turn_icon],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        ft.ElevatedButton(
                            "タイトルへ戻る",
                            on_click=self.go_to_title,
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
                bgcolor="#80000000",
                visible=False, 
            )

            self.your_turn_image = ft.Image(
                src="/your_turn.png",
                width=400,
                height=120,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            )
            self.cpu_turn_image = ft.Image(
                src="/cpu_turn.png",
                width=400,
                height=120,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            )
            
            self.difficulty_game_icon = ft.Image(
                src=DIFFICULTY_ICONS.get(self.level, DIFFICULTY_ICONS["easy"]),
                width=300, height=90, fit=ft.ImageFit.CONTAIN
            )
            self.turn_game_icon = ft.Image(
                src=TURN_ICONS.get(self.player_color, TURN_ICONS["black"]),
                width=90, height=90, fit=ft.ImageFit.CONTAIN
            )
            self.info_container = ft.Container(
                content=ft.Column(
                    controls=[self.difficulty_game_icon, self.turn_game_icon],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                right=20, top=20,
            )

            self.turn_indicator_container = ft.Container(
                content=ft.Stack([self.your_turn_image, self.cpu_turn_image]),
                top=20,
                left=20,
                padding=5,
            )

            othello_board_ui = self.makeOthelloBoard()
            
            self.start_button_container = ft.Container( 
                content=self.start_button,
                alignment=ft.alignment.center,
                expand=True
            )
            
            self.main_stack_controls = [
                othello_board_ui,
                self.turn_indicator_container,
                self.info_container,
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
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        except Exception as e:
            with open("gameview_error.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
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
        if self.result_overlay.visible:
             self.your_turn_image.visible = False
             self.cpu_turn_image.visible = False
        current_page.update()

    def on_click_start_game(self, e):
        self.page_ref.update()
        self.game = Othello(
            self.white_stones,
            self.black_stones,
            self.can_put_dots,
            self.ai_player_number
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
            if level == "easy": self.game.ai_move(current_page)
            elif level == "normal": self.game.monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "hard": self.game.upgraded_monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "master": self.game.alpha_beta_ai_move(current_page, depth=5)
            elif level == "oni": self.game.hybrid_ai_move(current_page, depth=5, switch_ai_moves=11)
            print(f"DEBUG VIEW: AI logic call finished. Current game turn: {self.game.turn}")
            self.update_turn_indicator()
        else:
            print(f"DEBUG VIEW: Now Player's turn ({self.player_color}). Game turn: {self.game.turn}")
            self.update_turn_indicator()

    def makeOthelloBoard(self):
        current_page = self.page_ref
        board_length = current_page.height * 0.8 
        grid_size = board_length / settings.BOARD_SIZE
        container = ft.Container(height=current_page.height, width=current_page.width, bgcolor="#77e0d9")
        board_container = ft.Container(height=board_length + 20, width=board_length + 20)
        board_green = ft.Container(height=board_length + 2, width=board_length + 2, bgcolor='#299643')
        board_shade = ft.Container(height=board_length + 20, width=board_length + 20, bgcolor="#B36C3E", top=0, left=0, border_radius=10)
        board_vertical_lines = [ft.Container(height=board_length+2, width=2, bgcolor='#000000', top=0, left=i * grid_size) for i in range(settings.BOARD_SIZE + 1)]
        board_horizontal_lines = [ft.Container(height=2, width=board_length+2, bgcolor='#000000', top=i * grid_size, left=0) for i in range(settings.BOARD_SIZE + 1)]
        dots = [ft.Container(height=8, width=8, bgcolor='#000000', top=i * grid_size - 3, left=j * grid_size - 3, border_radius=5) for i in [settings.BOARD_SIZE//3, settings.BOARD_SIZE*2//3] for j in [settings.BOARD_SIZE//3, settings.BOARD_SIZE*2//3]]
        white_disc_front = ft.Container(height=grid_size * 8 / 10, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#fafafa')
        white_disc_back = ft.Container(height=grid_size * 83 / 100, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#141212')
        white_discs = [ft.Stack(controls=[white_disc_back, white_disc_front], top=grid_size * row + grid_size * 1 / 10, left=grid_size * column + grid_size * 1 / 10, visible=False, ref=self.white_stones[row][column]) for row in range(settings.BOARD_SIZE) for column in range(settings.BOARD_SIZE)]
        black_disc_front = ft.Container(height=grid_size * 8 / 10, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#141212')
        black_disc_back = ft.Container(height=grid_size * 83 / 100, width=grid_size * 8 / 10, border_radius=grid_size, bgcolor='#fafafa')
        black_discs = [ft.Stack(controls=[black_disc_back, black_disc_front], top=grid_size * row + grid_size * 1 / 10, left=grid_size * column + grid_size * 1 / 10, visible=False, ref=self.black_stones[row][column]) for row in range(settings.BOARD_SIZE) for column in range(settings.BOARD_SIZE)]
        click_areas_list = []
        for row_idx in range(settings.BOARD_SIZE):
            for col_idx in range(settings.BOARD_SIZE):
                btn = ft.CupertinoButton("T",
                    height=grid_size * 9 / 10, width=grid_size * 9 / 10, opacity=0,
                    top=grid_size * row_idx + grid_size * 1 / 20, left=grid_size * col_idx + grid_size * 1 / 20,
                    ref=self.click_areas[row_idx][col_idx],
                    on_click=lambda e, r=row_idx, c=col_idx: self.handle_player_move(r, c) 
                )
                click_areas_list.append(btn)
        can_put_dots_list = []
        for row in range(settings.BOARD_SIZE):
            for column in range(settings.BOARD_SIZE):
                dot = ft.Container(height=grid_size * 2 / 10, width=grid_size * 2 / 10, bgcolor="#FFF671", border_radius=grid_size * 1 / 10, top=grid_size * row + grid_size * 4 / 10, left=grid_size * column + grid_size * 4 / 10, visible=False, ref=self.can_put_dots[row][column])
                can_put_dots_list.append(dot)
        othello = ft.Stack(controls=[board_green, *board_vertical_lines, *board_horizontal_lines, *dots, *white_discs, *black_discs, *can_put_dots_list, *click_areas_list], top=10, left=10)
        othello_stack = ft.Stack(controls=[board_container, board_shade, othello])
        stack = ft.Stack(controls=[container, othello_stack])
        return stack
    
    def handle_player_move(self, r, c):
        current_page = self.page_ref
        player_turn_in_controller = 1 if self.player_color == "white" else 2
        if self.game.turn == player_turn_in_controller:
            if (r,c) in self.game.can_put_area(self.game.turn):
                self.game.put_stone(r, c, current_page)
                self.update_turn_indicator()
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
        
        self.your_turn_image.visible = False
        self.cpu_turn_image.visible = False
        
        print("DEBUG VIEW: Result overlay visible set to True. Updating page.")
        current_page_obj.update()

    def go_to_title(self, e): 
        current_page_obj = self.page_ref 
        print(f"DEBUG VIEW: go_to_title called on page {id(current_page_obj)}")
        self.result_overlay.visible = False
        current_page_obj.update() 
        current_page_obj.go("/")