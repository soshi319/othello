import random

class BaseAI:
    def __init__(self, ctrl):
        self.ctrl = ctrl

    def get_move(self):
        raise NotImplementedError

    def get_legal_move_list(self, legal_board):
        moves = []
        temp = legal_board
        while temp:
            move = temp & -temp
            moves.append(move)
            temp &= temp - 1
        return moves
    
    def _get_flipped_board(self, move_bit, player_board, opponent_board):
        flipped_stones = 0
        for shift, mask, is_left in self.ctrl.DIRECTIONS:
            temp_flipped = 0
            
            if is_left:
                temp = (move_bit << shift) & mask & opponent_board
            else:
                temp = (move_bit >> shift) & mask & opponent_board
            
            while temp != 0:
                temp_flipped |= temp
                if is_left:
                    temp = (temp << shift) & mask & opponent_board
                else:
                    temp = (temp >> shift) & mask & opponent_board
            
            if is_left:
                is_ok = (temp_flipped << shift) & mask & player_board
            else:
                is_ok = (temp_flipped >> shift) & mask & player_board
        
            if is_ok != 0:
                flipped_stones |= temp_flipped
        
        return flipped_stones

    def _simulate_random_playout(self, player_board, opponent_board, current_turn):
        sim_p_board = player_board
        sim_o_board = opponent_board
        sim_turn = current_turn

        passes = 0
        while passes < 2:
            legal_board = self.ctrl.get_legal_moves(sim_p_board, sim_o_board)
            
            if legal_board == 0:
                passes += 1
                sim_turn = 3 - sim_turn
                sim_p_board, sim_o_board = sim_o_board, sim_p_board
                continue
                
            passes = 0
            moves = self.get_legal_move_list(legal_board)
            move = random.choice(moves)
            
            flipped = self._get_flipped_board(move, sim_p_board, sim_o_board)
            
            sim_p_board ^= move | flipped
            sim_o_board ^= flipped
            
            sim_turn = 3 - sim_turn
            sim_p_board, sim_o_board = sim_o_board, sim_p_board

        p_count = bin(sim_p_board).count('1')
        o_count = bin(sim_o_board).count('1')
        
        if p_count > o_count:
            return sim_turn
        elif o_count > p_count:
            return 3 - sim_turn
        else:
            return 0


