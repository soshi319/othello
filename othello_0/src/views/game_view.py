import os
import sys
import flet as ft # type: ignore

# 盤面サイズ
BOARD_SIZE = 6

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.controller.othello_controller import Othello
from src.data.white_stones import WhiteStones
from src.data.black_stones import BlackStones
from src.data.can_put_dots import CanPutDots

class GameView(ft.View):
    def __init__(self, page, route):
        self.white_stones = WhiteStones.white_stones
        self.black_stones = BlackStones.black_stones
        self.can_put_dots = CanPutDots.can_put_dots
        self.click_areas = [[ft.Ref[ft.Stack]() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game = Othello()
        self.page = page

        super().__init__(
            route,
            [
                self.makeOthelloBoard(page),
                ft.ElevatedButton("start Game", on_click=self.on_click_start_game),
            ],
        )

    def on_click_start_game(self, e):
        self.game.start_game()
        self.page.update()

    def makeOthelloBoard(self, page):
        board_length = page.height * 0.8
        grid_size = board_length / BOARD_SIZE

        # ボードの外側
        container = ft.Container(
            height=page.height * 8 / 10,
            width=board_length,
            bgcolor='#ffffff',
        )

        # ボードをまとめる用
        board_container = ft.Container(
            height=board_length + 1,
            width=board_length + 1,
            bgcolor='#ffffff',
        )

        # ボードの緑のところ
        board_green = ft.Container(
            height=board_length + 1,
            width=board_length + 1,
            bgcolor='#30AD30',
        )

        # ボードの影
        board_shade = ft.Container(
            height=board_length,
            width=board_length,
            bgcolor='#404040',
            top=0,
            left=0,
        )

        # ボードの縦線
        board_vertical_lines = [
            ft.Container(
                height=board_length,
                width=1,
                bgcolor='#000000',
                top=0,
                left=i * grid_size,
            )
            for i in range(BOARD_SIZE + 1)
        ]

        # 横線
        board_horizontal_lines = [
            ft.Container(
                height=1,
                width=board_length,
                bgcolor='#000000',
                top=i * grid_size,
                left=0,
            )
            for i in range(BOARD_SIZE + 1)
        ]


        # 点（6×6の場合は標準ルール上は中央4点なので調整推奨）
        dots = [
            ft.Container(
                height=5,
                width=5,
                bgcolor='#000000',
                top=i * grid_size - 2,
                left=j * grid_size - 2,
                border_radius=5,
            )
            for i in [2, 4]
            for j in [2, 4]
        ]

        # 白い駒
        white_disc_front = ft.Container(
            height=grid_size * 8 / 10,
            width=grid_size * 8 / 10,
            border_radius=grid_size,
            bgcolor='#fafafa',
        )
        white_disc_back = ft.Container(
            height=grid_size * 83 / 100,
            width=grid_size * 8 / 10,
            border_radius=grid_size,
            bgcolor='#141212',
        )

        white_discs = [
            ft.Stack(
                controls=[
                    white_disc_back,
                    white_disc_front,
                ],
                top=grid_size * row + grid_size * 1 / 10,
                left=grid_size * column + grid_size * 1 / 10,
                visible=False,
                ref=self.white_stones[row][column]
            )
            for row in range(BOARD_SIZE)
            for column in range(BOARD_SIZE)
        ]

        # 黒い駒
        black_disc_front = ft.Container(
            height=grid_size * 8 / 10,
            width=grid_size * 8 / 10,
            border_radius=grid_size,
            bgcolor='#141212',
        )

        black_disc_back = ft.Container(
            height=grid_size * 83 / 100,
            width=grid_size * 8 / 10,
            border_radius=grid_size,
            bgcolor='#fafafa',
        )

        black_discs = [
            ft.Stack(
                controls=[
                    black_disc_back,
                    black_disc_front,
                ],
                top=grid_size * row + grid_size * 1 / 10,
                left=grid_size * column + grid_size * 1 / 10,
                visible=False,
                ref=self.black_stones[row][column]
            )
            for row in range(BOARD_SIZE)
            for column in range(BOARD_SIZE)
        ]

        # クリック判定
        click_areas = []
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                btn = ft.CupertinoButton("T",
                    height=grid_size * 9 / 10,
                    width=grid_size * 9 / 10,
                    bgcolor="#F700FF",
                    top=grid_size * row + grid_size * 1 / 20,
                    left=grid_size * column + grid_size * 1 / 20,
                    opacity=0,
                    ref=self.click_areas[row][column],
                    on_click=lambda e, r=row, c=column: self.game.put_stone(r, c, page)
                )
                click_areas.append(btn)

        # 置ける場所の表示
        can_put_dots = []
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                dot = ft.Container(
                    height=grid_size * 2 / 10,
                    width=grid_size * 2 / 10,
                    bgcolor="#FFF671",
                    border_radius=grid_size * 1 / 10,
                    top=grid_size * row + grid_size * 4 / 10,
                    left=grid_size * column + grid_size * 4 / 10,
                    visible=False,
                    ref=self.can_put_dots[row][column],
                )
                can_put_dots.append(dot)

        othello = ft.Stack(
            controls=[
                board_container,
                board_shade,
                board_green,
                *board_vertical_lines,
                *board_horizontal_lines,
                *dots,
                *white_discs,
                *black_discs,
                *can_put_dots,
                *click_areas,
            ],
        )

        stack = ft.Stack(
            controls=[
                container,
                othello,
            ],
            alignment=ft.alignment.center,
        )

        return stack
