import random
from ai.base_ai import BaseAI

class NormalAI(BaseAI):
    def get_move(self):
        if self.ctrl.turn == 1:
            player_board = self.ctrl.black_board
            opponent_board = self.ctrl.white_board
        else:
            player_board = self.ctrl.white_board
            opponent_board = self.ctrl.black_board
        
        legal_board = self.ctrl.get_legal_moves(player_board, opponent_board)
        moves = self.get_legal_move_list(legal_board)
        
        if not moves:
            return None
            
        return random.choice(moves)