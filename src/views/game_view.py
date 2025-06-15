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
            width = page_arg.width
            height = page_arg.height
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
                content=ft.Text("START", size=width // 60, weight=ft.FontWeight.BOLD),
                on_click=self.on_click_start_game,
                style=self.button_style1,
                height=height // 13, width=width // 8
            )
            
            # ▼▼▼【変更箇所】結果表示のUI定義を最初の状態に戻します ▼▼▼
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
                height=height,
                width=width,
            )
            # ▲▲▲【変更箇所】ここまで ▲▲▲

            self.your_turn_image = ft.Image(
                src="/your_turn.png",
                width=width // 5,
                height=height // 8,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            )
            self.cpu_turn_image = ft.Image(
                src="/cpu_turn.png",
                width=width // 5,
                height=height // 8,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            )
            
            self.difficulty_game_icon = ft.Image(
                src=DIFFICULTY_ICONS.get(self.level, DIFFICULTY_ICONS["easy"]),
                width=width // 5, height=height // 8, fit=ft.ImageFit.CONTAIN
            )
            self.turn_game_icon = ft.Image(
                src=TURN_ICONS.get(self.player_color, TURN_ICONS["black"]),
                width=width // 18, height=width // 18, fit=ft.ImageFit.CONTAIN
            )
            self.info_container = ft.Container(
                content=ft.Column(
                    controls=[self.difficulty_game_icon, self.turn_game_icon],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                right=height * 0.02,
                top=height * 0.02,
            )

            self.turn_indicator_container = ft.Container(
                content=ft.Stack([self.your_turn_image, self.cpu_turn_image]),
                left=height * 0.02,
                top=height * 0.02,
                padding=5,
            )

            othello_board_ui = self.makeOthelloBoard()
            
            button_width = width // 8
            self.start_button_container = ft.Container( 
                content=self.start_button,
                top=height * 0.45,
                left=(width - button_width) / 2
            )
            
            # ▼▼▼【変更箇所】main_stack_controlsの定義を最初の状態に戻します ▼▼▼
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
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            # ▲▲▲【変更箇所】ここまで ▲▲▲

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
        self.your_turn_image.visible = is_player_turn
        self.cpu_turn_image.visible = not is_player_turn
        if self.result_overlay.visible:
             self.your_turn_image.visible = False
             self.cpu_turn_image.visible = False
        current_page.update()

    # ▼▼▼【変更箇所】スタートボタン削除ロジックを最初の状態に戻します ▼▼▼
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
    # ▲▲▲【変更箇所】ここまで ▲▲▲

    def try_ai_move(self):
        current_page = self.page_ref
        ai_turn_in_controller = self.game.ai_player_number
        if self.game.turn == ai_turn_in_controller:
            level = getattr(current_page, "level", "easy")
            if level == "easy": self.game.ai_move(current_page)
            elif level == "normal": self.game.monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "hard": self.game.upgraded_monte_carlo_ai_move(current_page, num_simulations=100)
            elif level == "master": self.game.alpha_beta_ai_move(current_page, depth=5)
            elif level == "oni": self.game.hybrid_ai_move(current_page, depth=5, switch_ai_moves=11)
            self.update_turn_indicator()
        else:
            self.update_turn_indicator()

    def makeOthelloBoard(self):
        current_page = self.page_ref
        width = current_page.width
        height = current_page.height
        
        board_length = height * 0.8 
        padding = height * 0.022
        radius = padding / 2
        
        grid_size = board_length / settings.BOARD_SIZE
        
        background_container = ft.Container(height=height, width=width, bgcolor="#77e0d9")
        
        board_container_width = board_length + padding
        board_container_height = board_length + padding
        
        board_container = ft.Container(height=board_container_height, width=board_container_width)
        board_green = ft.Container(height=board_length + 2, width=board_length + 2, bgcolor='#299643')
        board_shade = ft.Container(height=board_container_height, width=board_container_width, bgcolor="#B36C3E", top=0, left=0, border_radius=radius)
        
        board_vertical_lines = [ft.Container(height=board_length+2, width=2, bgcolor='#000000', top=0, left=i * grid_size) for i in range(settings.BOARD_SIZE + 1)]
        board_horizontal_lines = [ft.Container(height=2, width=board_length+2, bgcolor='#000000', top=i * grid_size, left=0) for i in range(settings.BOARD_SIZE + 1)]

        dots = [ft.Container(height=8, width=8, bgcolor='#000000', top=i * grid_size - 4, left=j * grid_size - 4, border_radius=4) for i in [settings.BOARD_SIZE//4, settings.BOARD_SIZE*3//4] for j in [settings.BOARD_SIZE//4, settings.BOARD_SIZE*3//4]]        
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

        othello_inner = ft.Stack(controls=[board_green, *board_vertical_lines, *board_horizontal_lines, *dots, *white_discs, *black_discs, *can_put_dots_list, *click_areas_list], top=padding/2, left=padding/2)
        othello_board_stack = ft.Stack(controls=[board_container, board_shade, othello_inner])
        
        centered_board_container = ft.Container(
            content=othello_board_stack,
            width=board_container_width,
            height=board_container_height,
            top=(height - board_container_height) / 2,
            left=(width - board_container_width) / 2,
        )

        return ft.Stack(controls=[background_container, centered_board_container])
    
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
        
        player_score = white_count if self.player_color == 'white' else black_count
        cpu_score = black_count if self.player_color == 'white' else white_count
        
        score_text = f"あなた ({self.player_color}): {player_score}  CPU ({self.ai_color}): {cpu_score}"
        
        result_message = ""
        player_won = (self.player_color == 'white' and white_count > black_count) or \
                     (self.player_color == 'black' and black_count > white_count)
        
        if player_score == cpu_score:
            result_message = "引き分け！"
        elif player_won:
            result_message = "あなたの勝ち！"
        else:
            result_message = "あなたの負け"

        self.result_text_control.value = result_message
        self.result_score_control.value = score_text
        self.result_overlay.visible = True
        
        self.your_turn_image.visible = False
        self.cpu_turn_image.visible = False
        
        current_page_obj.update()

    def go_to_title(self, e): 
        current_page_obj = self.page_ref 
        self.result_overlay.visible = False
        current_page_obj.update() 
        current_page_obj.go("/")