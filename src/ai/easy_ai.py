import settings
from ai.base_ai import BaseAI

class EasyAI(BaseAI):
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
        
        worst_winrate = 1
        worst_move = moves[0]

        num_simulations = settings.AI_SIMULATIONS_HARD[settings.BOARD_SIZE]
        sims_per_move = max(1, num_simulations // len(moves))

        for move in moves:
            wins = 0
            flipped = self._get_flipped_board(move, player_board, opponent_board)
            next_p_board = opponent_board ^ flipped
            next_o_board = player_board ^ (move | flipped)
            next_turn = 3 - self.ctrl.turn

            for _ in range(sims_per_move):
                winner = self._simulate_random_playout(next_p_board, next_o_board, next_turn)
                if winner == self.ctrl.turn:
                    wins += 1

            winrate = wins / sims_per_move
            if winrate < worst_winrate:
                worst_winrate = winrate
                worst_move = move

        return worst_move