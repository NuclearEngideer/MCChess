import chess
import chess.pgn
import re
import random
import copy
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(levelname)s:%(message)s',
                    filename="debug.log")

def write_intro():
    print('This is a basic monte carlo chess engine. You play as white.\n'
          'Enter your moves when prompted in UCI format.\n'
          'For example, moving the e2 pawn to e4 would be entered at\n'
          'the prompt as: e2e4\n'
          'A promotion of a pawn would be "a7a8q" for promotion to Queen.\n')

def get_human_move(board):
    legal_move = False
    getting_input = True
    while not legal_move:
        while getting_input:
            move = input('Enter UCI move for white: ').lower()
            if re.match(r'\D\d\D\d[q|r|n|b]?', move):
                getting_input = False
            else:
                print('Could not parse move. Check your UCI entry and try again.')
        if chess.Move.from_uci(move) in board.legal_moves:
            board.push(chess.Move.from_uci(move))
            legal_move = True
        else:
            print('Illegal move, please enter a legal move.')
            getting_input = True

def print_board(board):
    rank = 8
    board_string = '\n'
    for line in board.unicode().split('\n'):
        if line:
            board_string +=f'{rank} ' + line + '\n'
            rank -= 1
    board_string += '  A B C D E F G H\n'
    print(board_string)

class MCEngine():
    # TODO: Add logic to deal with checkmate 
    # TODO: Generate some form of importance function
    # TODO: Add the multiple sublines and depth feature to the random moves
    
    def __init__(self, board, depth, num_lines, global_moves):
        self.board = board # The current board, either from player input or from random move
        self.global_moves = global_moves # The number of global moves so far, either from player input or from random move
        self.depth = depth # The targeted move depth of the engine
        self.stop_move_number = global_moves + depth # The targeted move number to stop at
        self.num_lines = num_lines # The number of LGs this class initializes
        # self.start_line_generator()


    def line_generator(self):
        results = {}
        # positions = []
        initial_position = copy.deepcopy(self.board)
        positions = self._recursive_mc_moves(initial_position, 0, initial_position.fullmove_number)
        # Uncomment below for accidentally extra lines
        # for line in range(self.num_lines):
        #     print(f'working on line {line+1}')
        #     mc_positions = self._recursive_mc_moves(initial_position, 0, line)
        #     results[line]=mc_positions
        #     positions += mc_positions
        # for key, value in results.items():
        #     print(f'In Line {key+1}, movestacks are:')
        #     for move in value:
        #         print(move.move_stack)
        positions = self.remove_duplicate_positions(positions)
        logging.debug(initial_position.fullmove_number)
        # TODO: this will just choose a random move. Needs an importance function still
        self.initialize_prng(initial_position, initial_position.fullmove_number, 8675309)
        selected_line = positions[random.randrange(0, len(positions))]
        selected_move = selected_line.move_stack[self.board.fullmove_number*2 -1]
        print(f'Computer plays: {self.board.san(selected_move)}')
        self.board.push(selected_line.move_stack[self.board.fullmove_number*2 - 1])
        

    def initialize_prng(self, current_position, move_number, line_number):
            board_map = current_position.piece_map()
            seed = 0
            for key, value in board_map.items():
                match value.symbol().lower():
                    case 'k':
                        pv = 100
                    case 'q':
                        pv = 9
                    case 'r':
                        pv = 5
                    case 'b' | 'n':
                        pv = 3
                    case 'p':
                        pv = 1
                seed += key*pv
            seed += move_number* line_number
            logging.debug(seed)
            random.seed(seed)

    def random_move(self, current_board):
        if current_board.legal_moves.count()>1:
            random_move_index = random.randrange(0, current_board.legal_moves.count()-1)
        elif current_board.legal_moves.count()==1:
            random_move_index = 0
        legal_moves = [move for move in current_board.legal_moves]
        selected_move = legal_moves[random_move_index]
        logging.debug(f'{selected_move}')
        current_board.push(selected_move)
        return copy.deepcopy(current_board)

    def _recursive_mc_moves(self, starting_position, depth, line):
        # starting position is board class
        logging.debug(depth)
        if depth == self.depth:
            return [copy.deepcopy(starting_position)]
        
        results = []

        # Handle checkmate and stalemate
        if starting_position.is_checkmate() or starting_position.is_stalemate():
            results.extend([copy.deepcopy(starting_position)])
            return results
        
        for i in range(self.num_lines):
            self.initialize_prng(starting_position, starting_position.fullmove_number, i+depth+line)
            current_board = self.random_move(copy.deepcopy(starting_position))
            logging.debug(current_board.unicode())
            result = self._recursive_mc_moves(current_board, depth+1, i)
            results.extend(result)
        
        return results

    def remove_duplicate_positions(self, position_list:list):
        unique_positions = []
        for position in position_list:
            if not any(position == existing_position for existing_position in unique_positions):
                unique_positions.append(position)
        return unique_positions

    def is_good_position(self):
        # Want to check how good each positioin is
        # Count the attackers on a piece and if other pieces are defending it?
        pass

def main():
    # odd depths end back on white's turn
    depth = 5
    num_lines = 4
    checkmate = False
    write_intro()

    # Can provide an FEN here to set a starting position. Default to standard for now
    # Could easily do arg parsing for more in depth. Let's get the actual engine underway for now.

    # Note, can print pgn for an analysis engine via print(game.from_board(board))

    board = chess.Board()
    print_board(board)
    while not checkmate:
        # Calculate legal moves for the pieces
        get_human_move(board)
        print_board(board)
        
        if not board.is_checkmate() or not board.is_stalemate():
            MCE = MCEngine(board, depth = depth, num_lines = num_lines, global_moves=board.fullmove_number)
            MCE.line_generator()
            print_board(board)
        else:
            print('checkmate (or stalemate ig)')


if __name__ == "__main__":
    main()