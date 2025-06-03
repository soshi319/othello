import os
import sys
import flet as ft # type: ignore

# 盤面サイズ
BOARD_SIZE = 6

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.controller.othello_controller import Othello # othello_controller.py (10番目のファイル) を参照
from src.data.white_stones import WhiteStones
from src.data.black_stones import BlackStones
from src.data.can_put_dots import CanPutDots

class GameView(ft.View):
    def __init__(self, page, route):
        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.page = page
        self.player_color = getattr(page, "player_color", "black") # select_turn_view から渡される
        self.ai_color = "white" if self.player_color == "black" else "black"

        self.game = Othello() # OthelloController の __init__ は引数を取らない古い形式

        # ★★★ プレイヤーの色に応じて、ゲーム開始時の手番をOthelloインスタンスに設定 ★★★
        # OthelloController側の self.turn は「現在の手番」を示す
        # プレイヤーが黒 (先手) の場合、ゲームの最初のターンは黒 (2)
        # プレイヤーが白 (後手) の場合、ゲームの最初のターンはAI (黒 = 2)
        # OthelloControllerのデフォルトが self.turn = 2 なので、
        # プレイヤーが黒を選んだ場合はそのままで良い。
        # プレイヤーが白を選んだ場合、AIが黒で先手なので、これもそのままで良い。
        # ただし、try_ai_move が正しくAIの手番を判定する必要がある。

        # スタートボタンの定義と配置 (中央配置に戻すことを推奨)
        self.start_button = ft.ElevatedButton(
            "START",
            on_click=self.on_click_start_game,
            style=ft.ButtonStyle( 
                bgcolor="#FFFFFF",
                color="#000000",
                overlay_color="#818181",
                padding=ft.padding.all(20),
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)
            ),
            height=70,
            width=250
        )
        
        self.start_button_container = ft.Container(
            content=self.start_button,
            alignment=ft.alignment.center, 
            expand=True  
        )
        
        othello_board_ui = self.makeOthelloBoard(page)
        super().__init__(
            route,
            [
                ft.Stack( 
                    controls=[
                        othello_board_ui, 
                        self.start_button_container  # ←名前つきで追加！
                    ],
                    expand=True 
                )
            ]
        )

    def on_click_start_game(self, e):
        self.game.start_game()
        # ...ヒント等の更新...
        # Stackからボタンコンテナを除外する（可視性でなく、完全にremove）
        self.controls[0].controls.remove(self.start_button_container)
        self.page.update()
        self.try_ai_move()

    def try_ai_move(self):
        # AIの色に対応する手番番号
        ai_turn_number_for_logic = 1 if self.ai_color == "white" else 2
        
        # ★★★ 現在の手番がAIの手番であればAIを動かす ★★★
        if self.game.turn == ai_turn_number_for_logic:
            print(f"AI ({self.ai_color}) is thinking... Current turn: {self.game.turn}")
            level = getattr(self.page, "level", "easy")
            if level == "easy":
                self.game.ai_move(self.page)
            elif level == "normal":
                self.game.monte_carlo_ai_move(self.page, num_simulations=100)
            elif level == "hard":
                self.game.monte_carlo_ai_move(self.page, num_simulations=500)
            elif level == "master":
                self.game.monte_carlo_ai_move(self.page, num_simulations=1000)
        # else:
            # print(f"Not AI's turn. Game turn: {self.game.turn}, AI is {self.ai_color} (expects turn {ai_turn_number_for_logic})")


    def makeOthelloBoard(self, page):
        board_length = page.height * 0.8
        grid_size = board_length / BOARD_SIZE
        container = ft.Container(height=page.height, width=page.width, bgcolor="#7decff")
        board_container = ft.Container(height=board_length + 1, width=board_length + 1, bgcolor="#8c00ff")
        board_green = ft.Container(height=board_length + 1, width=board_length + 1, bgcolor='#30AD30')
        board_shade = ft.Container(height=board_length, width=board_length, bgcolor='#404040', top=0, left=0)
        board_vertical_lines = [ft.Container(height=board_length, width=1, bgcolor='#000000', top=0, left=i * grid_size) for i in range(BOARD_SIZE + 1)]
        board_horizontal_lines = [ft.Container(height=1, width=board_length, bgcolor='#000000', top=i * grid_size, left=0) for i in range(BOARD_SIZE + 1)]
        dots = [ft.Container(height=5, width=5, bgcolor='#000000', top=i * grid_size - 2, left=j * grid_size - 2, border_radius=5) for i in [2, 4] for j in [2, 4]]
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
                    height=grid_size * 9 / 10,
                    width=grid_size * 9 / 10,
                    # bgcolor="#F700FF",
                    opacity=0,
                    top=grid_size * row_idx + grid_size * 1 / 20,
                    left=grid_size * col_idx + grid_size * 1 / 20,
                    ref=self.click_areas[row_idx][col_idx],
                    # ★★★ クリック時の処理を handle_player_move に集約 ★★★
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
    
    # ★★★ handle_player_move メソッドを定義 ★★★
    def handle_player_move(self, r, c):
        player_turn_number_for_logic = 1 if self.player_color == "white" else 2
        
        print(f"DEBUG: Clicked ({r},{c}). Game turn: {self.game.turn}. Player color: {self.player_color} (expects logic turn: {player_turn_number_for_logic})")
        
        # 現在のゲームのターンが、論理的なプレイヤーのターンと一致するか確認
        if self.game.turn == player_turn_number_for_logic:
            # さらに、その場所に本当に置けるか OthelloController に確認させる
            # can_put_area は現在の self.game.turn の石を基準に置ける場所を返す
            if (r,c) in self.game.can_put_area(self.game.turn):
                print(f"DEBUG: Player is putting stone at ({r},{c})")
                self.game.put_stone(r, c, self.page) # 石を置く
                # put_stone の中でターンが変わり、ヒントも更新され、page.update()もされる
                # その後、AIの手番であればAIが動く
                self.try_ai_move() # put_stone の後でAIのターンか確認
            else:
                print(f"DEBUG: Cannot put at ({r},{c}). Valid moves: {self.game.can_put_area(self.game.turn)}")
        else:
            print(f"DEBUG: Not player's turn (or logic error). Click ignored.")