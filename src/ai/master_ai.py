import settings
from ai.base_ai import BaseAI

class MasterAI(BaseAI):
    def __init__(self, ctrl):
        super().__init__(ctrl)
        size = settings.BOARD_SIZE
        self.flattened_weights = [
            self.ctrl.weights[r][c] for r in range(size) for c in range(size)
        ]

        self.ttable = {}

        self.endgame_empty = settings.AI_CHANGE_TIME_MASTER[size]
    
    def _count_empty(self, p_board, o_board):
        count = settings.BOARD_SIZE ** 2 - (p_board | o_board).bit_count()
        return count

    def _evaluate_bitboard(self, p_board, o_board):
        p_score = 0
        o_score = 0
        weights = self.flattened_weights
        
        temp_p = p_board
        while temp_p:
            stone = temp_p & -temp_p
            p_score += weights[stone.bit_length() - 1]
            temp_p &= temp_p - 1
            
        temp_o = o_board
        while temp_o:
            stone = temp_o & -temp_o
            o_score += weights[stone.bit_length() - 1]
            temp_o &= temp_o - 1

        p_mob = self.ctrl.get_legal_moves(p_board, o_board).bit_count()
        o_mob = self.ctrl.get_legal_moves(o_board, p_board).bit_count()

        return (p_score - o_score) + 2 * (p_mob - o_mob)

    def _negamax(self, p_board, o_board, depth, alpha, beta, passes=0):
        cache_key = (p_board, o_board, depth, alpha, beta)
        if cache_key in self.ttable:
            return self.ttable[cache_key]
        
        if depth==0:
            return self._evaluate_bitboard(p_board, o_board)
        
        legal_board = self.ctrl.get_legal_moves(p_board, o_board)
        if legal_board == 0:
            if passes == 1:
                p_count = p_board.bit_count()
                o_count = o_board.bit_count()
                return (p_count - o_count) * 10000
            return -self._negamax(o_board, p_board, depth, -beta, -alpha, passes=1)
        
        moves = self.get_legal_move_list(legal_board)
        moves.sort(key=lambda m: self.flattened_weights[m.bit_length() - 1], reverse=True)
        
        best = -float('inf')
        for move in moves:
            flipped = self._get_flipped_board(move, p_board, o_board)
            next_p_board = o_board ^ flipped
            next_o_board = p_board ^ (move | flipped)
            val = -self._negamax(next_p_board, next_o_board, depth-1, -beta, -alpha, passes=0)

            best = max(best, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break

        self.ttable[cache_key] = best
        return best
    
    def _negamax_endgame(self, p_board, o_board, alpha, beta, passes=0):
        legal_board = self.ctrl.get_legal_moves(p_board, o_board)

        if legal_board == 0:
            if passes == 1:
                return p_board.bit_count() - o_board.bit_count()
            return -self._negamax_endgame(o_board, p_board, -beta, -alpha, passes=1)

        moves = self.get_legal_move_list(legal_board)
        moves.sort(key=lambda m: self.flattened_weights[m.bit_length() - 1], reverse=True)

        best = -float('inf')
        for move in moves:
            flipped = self._get_flipped_board(move, p_board, o_board)
            next_p = o_board ^ flipped
            next_o = p_board ^ (move | flipped)
            val = -self._negamax_endgame(next_p, next_o, -beta, -alpha, passes=0)

            best = max(best, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break

        return best

    def get_move(self):
        self.ttable.clear()

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

        best_val = -float('inf')
        best_move = moves[0]
        
        depth = settings.AI_DEPTH_MASTER[settings.BOARD_SIZE]
        moves.sort(key=lambda m: self.flattened_weights[m.bit_length() - 1], reverse=True)

        for move in moves:
            flipped = self._get_flipped_board(move, player_board, opponent_board)
            next_p_board = opponent_board ^ flipped
            next_o_board = player_board ^ (move | flipped)
            
            if self._count_empty(player_board, opponent_board) - 1 <= self.endgame_empty:
                val = -self._negamax_endgame(next_p_board, next_o_board, -float('inf'), float('inf'))
            else:
                val = -self._negamax(next_p_board, next_o_board, depth - 1, -float('inf'), float('inf'))
            
            if val > best_val:
                best_val = val
                best_move = move

        return best_move