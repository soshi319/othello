import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True' # ← この1行を追記します！
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import flet as ft # type: ignore
import settings

from views.title_view import TitleView
from views.select_board_size_view import SelectBoardSizeView
from views.game_view import GameView
from views.select_level_view import SelectLevelView
from views.select_turn_view import SelectTurnView
from views.init_settings_view import InitSettingsView
from views.records_view import RecordsView

def main(page: ft.Page):
  page.window_full_screen = True
  page.window_maximized = True
  
  page.padding = 0
  page.title = "オセロ"
  page.level = "easy"
  page.player_color = "black"

  page.is_ai_vs_ai = False
  page.ai_black_level = "easy"
  page.ai_white_level = "easy"


  def load_settings():
    try:
      if page.client_storage.contains_key("is_initialized"):
        val_select = page.client_storage.get("SELECT_BOARD")
        if val_select is not None: settings.SELECT_BOARD = val_select
        
        val_size = page.client_storage.get("BOARD_SIZE")
        if val_size is not None: settings.BOARD_SIZE = val_size
        
        val_wait = page.client_storage.get("AI_WAIT_TIME")
        if val_wait is not None: settings.AI_WAIT_TIME = val_wait
        
        for size in [6, 8]:
          v_easy = page.client_storage.get(f"AI_SIMULATIONS_EASY_{size}")
          if v_easy is not None: settings.AI_SIMULATIONS_EASY[size] = v_easy
          
          v_hard = page.client_storage.get(f"AI_SIMULATIONS_HARD_{size}")
          if v_hard is not None: settings.AI_SIMULATIONS_HARD[size] = v_hard
          
          v_master = page.client_storage.get(f"AI_DEPTH_MASTER_{size}")
          if v_master is not None: settings.AI_DEPTH_MASTER[size] = v_master
          
          v_oni = page.client_storage.get(f"AI_SIMULATIONS_ONI_{size}")
          if v_oni is not None: settings.AI_SIMULATIONS_ONI[size] = v_oni
          
          v_oni_c = page.client_storage.get(f"AI_UCB_C_ONI_{size}")
          if v_oni_c is not None: settings.AI_UCB_C_ONI[size] = v_oni_c
          
          v_switch = page.client_storage.get(f"AI_SWITCH_MOVES_ONI_{size}")
          if v_switch is not None: settings.AI_SWITCH_MOVES_ONI[size] = v_switch
          
        return True
    except Exception as e:
      print(f"DEBUG: settings load failed, using default values. Error: {e}")
      return False
    return False

  def route_change(e: ft.RouteChangeEvent):
    page.views.clear()
    
    if e.route == "/init_settings":
      page.views.append(InitSettingsView(page, e.route))
    elif e.route == "/select_board_size":
      page.views.append(SelectBoardSizeView(page, e.route))
    elif e.route == "/select_level":
      page.views.append(SelectLevelView(page, e.route))
    elif e.route == "/select_turn":
      page.views.append(SelectTurnView(page, e.route))
    elif e.route == "/select_ai":
      from views.select_ai_view import SelectAiView
      page.views.append(SelectAiView(page, e.route))
    elif e.route == "/records":
      page.views.append(RecordsView(page, e.route))
    elif e.route == "/othello":
      page.views.append(GameView(page, e.route))
    else:
      page.views.append(TitleView(page, "/"))
      
    page.update()

  def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  

  if load_settings():
      page.go("/")
  else:
      page.go("/init_settings")



ft.app(target=main, assets_dir="assets")