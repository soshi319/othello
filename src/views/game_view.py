import os
import sys
import traceback
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft # type: ignore

import settings
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

            ai_player_number_for_ctrl = 1 if self.ai_color == "black" else 2
            self.ai_player_number = ai_player_number_for_ctrl

            # AI同士の対戦（観戦モード）かどうかのフラグ
            self.is_ai_vs_ai = getattr(page_arg, "is_ai_vs_ai", False)
            
            # 有利不利（形勢）表示用のテキストコントロール（AI同士の時のみvisible=True）
            self.eval_text_control = ft.Text("形勢: 互角 (0)", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF", visible=False)
            
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
            
            self.result_text_control = ft.Text("結果計算中...", size=60, weight=ft.FontWeight.BOLD, color="#FFD700") 
            
            # アニメーション用のコンテナ
            self.animated_text_container = ft.Container(
                content=self.result_text_control,
                scale=ft.transform.Scale(0.1),
                animate_scale=ft.animation.Animation(800, ft.AnimationCurve.BOUNCE_OUT)
            )

            self.result_score_control = ft.Text("白: 0  黒: 0", size=36, color="#FFFFFF")
            self.result_difficulty_icon = ft.Image(
                src=DIFFICULTY_ICONS.get(self.level, DIFFICULTY_ICONS["easy"]),
                height=60, fit=ft.ImageFit.CONTAIN
            )
            self.result_turn_icon = ft.Image(
                src=TURN_ICONS.get(self.player_color, TURN_ICONS["black"]),
                height=60, fit=ft.ImageFit.CONTAIN
            )
            # 観戦モード用：勝者の難易度アイコンを大きく表示
            self.result_winner_icon = ft.Image(
                src="/level_easy.png",
                height=80, fit=ft.ImageFit.CONTAIN,
                visible=False
            )
            
            self.confetti_gif = ft.Image(
                src="/confetti.gif",
                width=width,
                height=height,
                fit=ft.ImageFit.CONTAIN,
                visible=False,
                scale=1,
            )

            self.unlock_hint_text = ft.Text(
                "", 
                size=15, 
                color="#B22222", 
                weight=ft.FontWeight.W_900, 
                text_align=ft.TextAlign.CENTER
            )

            self.unlock_hint = ft.Container(
                content=self.unlock_hint_text,
                border=ft.border.all(2, "#FFD700"), 
                border_radius=10,
                padding=10,
                bgcolor=ft.colors.with_opacity(0.9, "#FFFFFF"), 
                visible=False
            )

            self.result_overlay = ft.Container(
                content=ft.Stack([
                    self.confetti_gif,
                    ft.Container(
                        content=ft.Column(
                            [
                                self.animated_text_container,
                                self.result_winner_icon,
                                self.result_score_control,
                                self.unlock_hint,
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
                        alignment=ft.alignment.center,
                    )
                ]),
                alignment=ft.alignment.center, expand=True,
                bgcolor="#B3000000",
                visible=False,
                height=height,
                width=width,
            )

            # パス通知用UI
            self.pass_text = ft.Text(
                "Pass", 
                size=50, 
                weight=ft.FontWeight.W_600, 
                color=ft.colors.BLUE_700 
            )
            
            self.pass_container = ft.Container(
                content=self.pass_text,
                alignment=ft.alignment.center,
                bgcolor=ft.colors.with_opacity(0.4, ft.colors.WHITE), 
                border_radius=40, 
                padding=ft.padding.symmetric(vertical=20, horizontal=50),
                border=ft.border.all(2, ft.colors.BLUE_100), 
                shadow=ft.BoxShadow(
                    blur_radius=20,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                    spread_radius=1,
                ),
                visible=False,
                animate_opacity=300,
            )

            self.pass_overlay = ft.Container(
                content=self.pass_container,
                alignment=ft.alignment.center,
                expand=True,
                width=width,
                height=height,
                visible=False,
            )

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

            # 観戦モード用：黒番・白番の難易度アイコン
            if self.is_ai_vs_ai:
                ai_b_lvl = getattr(page_arg, "ai_black_level", "easy")
                ai_w_lvl = getattr(page_arg, "ai_white_level", "easy")
                self.black_turn_icon = ft.Image(
                    src=DIFFICULTY_ICONS.get(ai_b_lvl, "/level_easy.png"),
                    height=height // 8,
                    fit=ft.ImageFit.CONTAIN, visible=False
                )
                self.white_turn_icon = ft.Image(
                    src=DIFFICULTY_ICONS.get(ai_w_lvl, "/level_easy.png"),
                    height=height // 8,
                    fit=ft.ImageFit.CONTAIN, visible=False
                )
            else:
                self.black_turn_icon = ft.Image(src="/level_easy.png", visible=False)
                self.white_turn_icon = ft.Image(src="/level_easy.png", visible=False)

            self.turn_indicator_container = ft.Container(
                content=ft.Stack([
                    self.your_turn_image,
                    self.cpu_turn_image,
                    self.black_turn_icon,
                    self.white_turn_icon,
                ]),
                left=height * 0.02,
                top=height * 0.02,
                padding=5
            )

            # --- 観戦モードか通常モードかで右側インフォメーションUIを分岐 ---
            if self.is_ai_vs_ai:
                ai_b_lvl = getattr(page_arg, "ai_black_level", "easy")
                ai_w_lvl = getattr(page_arg, "ai_white_level", "easy")
                self.info_container = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("観戦モード", size=26, weight=ft.FontWeight.BOLD, color="#FFD700"),
                            ft.Container(height=5),
                            ft.Row([
                                ft.Text("先攻(黒):", color="#FFFFFF", weight=ft.FontWeight.BOLD, size=20),
                                ft.Image(src=DIFFICULTY_ICONS.get(ai_b_lvl, "/level_easy.png"), height=40, fit=ft.ImageFit.CONTAIN)
                            ], alignment=ft.MainAxisAlignment.END, spacing=8),
                            ft.Row([
                                ft.Text("後攻(白):", color="#FFFFFF", weight=ft.FontWeight.BOLD, size=20),
                                ft.Image(src=DIFFICULTY_ICONS.get(ai_w_lvl, "/level_easy.png"), height=40, fit=ft.ImageFit.CONTAIN)
                            ], alignment=ft.MainAxisAlignment.END, spacing=8),
                            ft.Container(height=15),
                            self.eval_text_control  # 観戦モードの時だけ形勢を配置
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    right=height * 0.02,
                    top=height * 0.02,
                    bgcolor="#B3111111",
                    padding=15,
                    border_radius=10,
                )
            else:
                self.difficulty_game_icon = ft.Image(src=DIFFICULTY_ICONS.get(self.level, DIFFICULTY_ICONS["easy"]), height=height // 8, fit=ft.ImageFit.CONTAIN)
                self.turn_game_icon = ft.Image(src=TURN_ICONS.get(self.player_color, TURN_ICONS["black"]), width=width // 18, height=width // 18, fit=ft.ImageFit.CONTAIN)
                self.info_container = ft.Container(
                    content=ft.Column(
                        controls=[self.difficulty_game_icon, self.turn_game_icon],  # 通常モードからは形勢表示を削除
                        spacing=8,
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    right=height * 0.02,
                    top=height * 0.02,
                )

            othello_board_ui = self.makeOthelloBoard()
            
            button_width = width // 8
            self.start_button_container = ft.Container( 
                content=self.start_button,
                top=height * 0.45,
                left=(width - button_width) / 2
            )

            # プレイ中用の「タイトルに戻る」ボタン
            self.back_to_title_button = ft.ElevatedButton(
                "タイトルへ",
                icon=ft.icons.HOME,
                on_click=self.go_to_title,
                bgcolor="#4A5568",
                color="#FFFFFF",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
            )

            self.back_button_container = ft.Container(
                content=self.back_to_title_button,
                left=height * 0.02,
                bottom=height * 0.02, 
            )
            
            self.main_stack_controls = [
                othello_board_ui,
                self.turn_indicator_container,
                self.info_container,
                self.start_button_container,
                self.back_button_container,
                self.pass_overlay,
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

    def render_board(self, black_board_bit, white_board_bit, legal_board_bit):
        """
        Controllerから渡されたビットボードの数値に基づいて、
        画面上のすべての石とドットの表示/非表示を一括で更新します。
        """
        is_player_turn = True
        if hasattr(self, 'game') and self.game:
            if self.game.turn == self.game.ai_player_number:
                is_player_turn = False

        if self.is_ai_vs_ai:
            is_player_turn = False


        for row in range(settings.BOARD_SIZE):
            for col in range(settings.BOARD_SIZE):
                pos = row * settings.BOARD_SIZE + col
                mask = 1 << pos
                
                # 黒石のUI更新
                if self.black_stones[row][col].current:
                    self.black_stones[row][col].current.visible = bool(black_board_bit & mask)
                
                # 白石のUI更新
                if self.white_stones[row][col].current:
                    self.white_stones[row][col].current.visible = bool(white_board_bit & mask)
                
                # 打てる場所の表示
                if self.can_put_dots[row][col].current:
                    if is_player_turn:
                        self.can_put_dots[row][col].current.visible = bool(legal_board_bit & mask)
                    else:
                        self.can_put_dots[row][col].current.visible = False
                    
        if self.page_ref:
            self.page_ref.update()

    def update_turn_indicator(self):
        current_page = self.page_ref
        if not current_page: return
        if not hasattr(self, 'game') or self.game is None: return

        if self.is_ai_vs_ai:
            # 観戦モード：黒番・白番の難易度アイコンを切り替え
            is_black_turn = (self.game.turn == 1)
            self.your_turn_image.visible = False
            self.cpu_turn_image.visible = False
            self.black_turn_icon.visible = is_black_turn and not self.result_overlay.visible
            self.white_turn_icon.visible = not is_black_turn and not self.result_overlay.visible
        else:
            # 通常モード：既存のまま
            player_turn_number_in_game_logic = 1 if self.player_color == "black" else 2
            is_player_turn = self.game.turn == player_turn_number_in_game_logic
            self.your_turn_image.visible = is_player_turn
            self.cpu_turn_image.visible = not is_player_turn
            self.black_turn_icon.visible = False
            self.white_turn_icon.visible = False
            if self.result_overlay.visible:
                self.your_turn_image.visible = False
                self.cpu_turn_image.visible = False

        current_page.update()

    def on_click_start_game(self, e):
        self.page_ref.update()
        
        # view_ref=self を渡してControllerが直接 render_board を呼べるようにする
        self.game = Othello(
            self.white_stones,
            self.black_stones,
            self.can_put_dots,
            self.ai_player_number,
            view_ref=self 
        )
        self.game.start_game()
        self.update_turn_indicator()
        if self.start_button_container in self.main_stack_controls:
            self.main_stack_controls.remove(self.start_button_container)
            if self.controls and isinstance(self.controls[0], ft.Stack):
                self.controls[0].controls = self.main_stack_controls
        self.page_ref.update()
        if self.is_ai_vs_ai:
            threading.Thread(target=self.run_ai_vs_ai, daemon=True).start()
        else:
            self.try_ai_move()

    def run_ai_vs_ai(self):
        """AI同士の対戦を自動進行させるループ"""
        current_page = self.page_ref
        while not self.result_overlay.visible:
            if self.game.turn == 1:
                difficulty = getattr(current_page, "ai_black_level", "easy")
            else:
                difficulty = getattr(current_page, "ai_white_level", "easy")
            
            self.game.execute_ai_move_by_difficulty(difficulty, current_page)
            self.update_turn_indicator()

    def try_ai_move(self):
        current_page = self.page_ref
        ai_turn_in_controller = self.game.ai_player_number
        
        while self.game.turn == ai_turn_in_controller:
            if self.result_overlay.visible:
                break

            level = getattr(current_page, "level", "easy")
            self.game.execute_ai_move_by_difficulty(level, current_page)
            self.update_turn_indicator()
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

        dots = [ft.Container(height=8, width=8, bgcolor='#000000', top=i * grid_size - 3, left=j * grid_size - 3, border_radius=4) for i in [settings.BOARD_SIZE//3, settings.BOARD_SIZE - settings.BOARD_SIZE//3] for j in [settings.BOARD_SIZE//3, settings.BOARD_SIZE - settings.BOARD_SIZE//3]]
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
        if not hasattr(self, 'game') or self.game is None:
            return
        
        current_page = self.page_ref
        player_turn_in_controller = 1 if self.player_color == "black" else 2
        
        if self.game.turn == player_turn_in_controller:
            success = self.game.put_stone(r, c, current_page)
            if success:
                self.update_turn_indicator()
                self.try_ai_move()

    def show_pass_ui(self):
        """パス通知を表示し、1.5秒後に非表示にする"""
        self.pass_overlay.visible = True
        self.pass_container.visible = True
        self.pass_container.opacity = 1
        if self.page_ref:
            self.page_ref.update()

        def hide_pass():
            if self.pass_container:
                self.pass_container.opacity = 0
            if self.page_ref:
                self.page_ref.update()
            import time
            time.sleep(0.3) # フェードアウト待ち
            if self.pass_overlay:
                self.pass_overlay.visible = False
            if self.page_ref:
                self.page_ref.update()

        threading.Timer(0.5, hide_pass).start()

    def show_result_ui(self, white_count, black_count): 
        current_page_obj = self.page_ref

        def hide_gif():
            self.confetti_gif.visible = False
            if self.page_ref:
                self.page_ref.update()

        if self.is_ai_vs_ai:
            ai_b_lvl = getattr(self.page_ref, "ai_black_level", "easy")
            ai_w_lvl = getattr(self.page_ref, "ai_white_level", "easy")

            if black_count > white_count:
                winner_lvl = ai_b_lvl
                self.result_text_control.value = "WIN!"
                self.result_text_control.color = "#FFD700"
            elif white_count > black_count:
                winner_lvl = ai_w_lvl
                self.result_text_control.value = "WIN!"
                self.result_text_control.color = "#FFD700"
            else:
                winner_lvl = None
                self.result_text_control.value = "引き分け！"
                self.result_text_control.color = "#FFFFFF"

            self.result_score_control.value = f"黒: {black_count}  白: {white_count}"
            self.result_difficulty_icon.src = DIFFICULTY_ICONS.get(ai_b_lvl, "/level_easy.png")
            self.result_turn_icon.src = DIFFICULTY_ICONS.get(ai_w_lvl, "/level_easy.png")

            # 勝者アイコンを大きく表示
            if winner_lvl:
                self.result_winner_icon.src = DIFFICULTY_ICONS.get(winner_lvl, "/level_easy.png")
                self.result_winner_icon.visible = True
            else:
                self.result_winner_icon.visible = False

            self.unlock_hint.visible = False
            self.confetti_gif.visible = False

        else:
            # 通常モードでは勝者アイコンを非表示
            self.result_winner_icon.visible = False

            player_score = white_count if self.player_color == 'white' else black_count
            cpu_score = black_count if self.player_color == 'white' else white_count

            color_dict = {"white":"白", "black":"黒"}
            self.result_score_control.value = f"あなた {color_dict[self.player_color]}: {player_score}  CPU {color_dict[self.ai_color]}: {cpu_score}"

            player_won = (self.player_color == 'white' and white_count > black_count) or \
                        (self.player_color == 'black' and black_count > white_count)

            if self.level == "master" and player_won:
                self.unlock_hint_text.value = "マスターに勝利！おめでとうございます。\n【挑戦状】かんたんに負けてみよう？！"
                self.unlock_hint.visible = True
            else:
                self.unlock_hint.visible = False

            if player_score == cpu_score:
                self.result_text_control.value = "引き分け！"
                self.result_text_control.color = "#FFFFFF"
                self.confetti_gif.visible = False
            elif player_won:
                self.result_text_control.value = "YOU WIN!!"
                self.result_text_control.color = "#FFD700"
                self.confetti_gif.visible = True
                threading.Timer(2.7, hide_gif).start()
            else:
                self.result_text_control.value = "YOU LOSE..."
                self.result_text_control.color = "#ADADAD"
                self.confetti_gif.visible = False

        self.result_overlay.visible = True
        self.your_turn_image.visible = False
        self.cpu_turn_image.visible = False
        self.black_turn_icon.visible = False
        self.white_turn_icon.visible = False
        current_page_obj.update()

        import time
        time.sleep(0.1)
        self.animated_text_container.scale = 1.0
        current_page_obj.update()

    def go_to_title(self, e): 
        current_page_obj = self.page_ref 
        self.result_overlay.visible = False
        self.confetti_gif.visible = False
        current_page_obj.is_ai_vs_ai = False  # タイトルに戻るときリセット
        current_page_obj.update() 
        current_page_obj.go("/")