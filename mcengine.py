import chess
import chess.pgn
import re
import random
import copy
import logging
import argparse
import time
import threading
from datetime import datetime, timezone

logging.basicConfig(level=logging.DEBUG, 
                    format='%(levelname)s:%(message)s',
                    filename="debug.log")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Monte Carlo Chess Engine of Dubious Quality")
    parser.add_argument("-d",
                        "--depth",
                        type=int,
                        default=5,
                        help="The depth to run the recursive search to")
    parser.add_argument("-n",
                        "--num_lines",
                        type=int,
                        default=4,
                        help="The number of lines from each node of the recursive tree")
    parser.add_argument('-w',
                        '--write_pgn',
                        type=bool,
                        default=True,
                        help='Flag to write PGN gamefile to a file.')
    return parser.parse_args()

def write_intro():
    print_logo()
    print('This is a basic Monte Carlo chess engine. You play as white.\n'
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

def print_logo():
    print('\n',
          '   __  ________        _______             \n',
          '  /  |/  / ___/ ____  / ___/ /  ___ ___ ___\n',
          ' / /|_/ / /__  /___/ / /__/ _ \/ -_|_-<(_-<\n',
          '/_/  /_/\___/        \___/_//_/\__/___/___/\n',
          '\n')

def thinking_animation(stop_signal):
    frames = ["Thinking /", "Thinking -", "Thinking \\", "Thinking |"]
    while not stop_signal.is_set():
        for frame in frames:
            if stop_signal.is_set():
                break
            print(f'\r{frame}', end='', flush=True)
            time.sleep(0.2)
    print('\r'+" "*20, end='', flush=True)

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
        if len(positions) > 1:
            self.initialize_prng(initial_position, initial_position .fullmove_number, 8675309)
            selected_line = positions[random.randrange(0, len(positions))]
        else:
            selected_line = positions[0]
        selected_move = selected_line.move_stack[self.board.fullmove_number*2 - 1]

        # TODO: this will just choose a random move. Needs an importance function still
        # position_strength = []
        # for position in positions:
        #     position_strength.append(self.is_good_position(position))
        # min_value = min(position_strength)
        # min_indices = [i for i, x in enumerate(position_strength) if x == min_value]
        # if len(min_indices) > 1:
        #     self.initialize_prng(initial_position, initial_position.fullmove_number, len(min_indices)*min_value)
        #     selected_line_index = min_indices[random.randrange(0, len(min_indices))]
        #     selected_line = positions[selected_line_index]
        #     selected_move = selected_line.move_stack[self.board.fullmove_number*2 - 1]
        # else:
        #     selected_line = positions[min_indices[0]]
        #     selected_move = selected_line.move_stack[self.board.fullmove_number*2 - 1]
        print(f'\rComputer plays: {self.board.san(selected_move)}')
        self.board.push(selected_move)
        # self.board.push(selected_line.move_stack[self.board.fullmove_number*2 - 1])
        

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

    def is_good_position(self, board):
        # Want to check how good each positioin is
        # Count the attackers on a piece and if other pieces are defending it?

        # Calculate score of pieces first. NEGATIVE SCORE IS GOOD FOR BLACK
        score = 0
        score += self.material_score(board)
        score += self.center_control(board)
        score += self.castling_rights(board)
        score += self.attacker_score(board)
        score += self.king_threat_score(board)
        return score
    
    def material_score(self, board):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        material_score = 0
        for piece_type in piece_values:
            material_score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            material_score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
        return material_score
    
    def center_control(self, board):
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        almost_center_squares = [chess.C4, chess.C5, chess.F4, chess.F5]
        center_score = 0
        for square in center_squares:
            attackers_white = len(board.attackers(chess.WHITE, square))
            attackers_black = len(board.attackers(chess.BLACK, square))
            center_score += attackers_white - attackers_black
        for square in almost_center_squares:
            attackers_white = len(board.attackers(chess.WHITE, square))
            attackers_black = len(board.attackers(chess.BLACK, square))
            center_score += 0.75 * (attackers_white - attackers_black)
        return center_score

    def castling_rights(self, board):
        castling_score = 0
        if board.has_kingside_castling_rights(chess.WHITE) or board.has_queenside_castling_rights(chess.WHITE):
            castling_score += 20
        if board.has_kingside_castling_rights(chess.BLACK) or board.has_queenside_castling_rights(chess.BLACK):
            castling_score -= 20
        return castling_score

    def attacker_score(self, board):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        attackers_score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type is not chess.KING:
                attackers = len(board.attackers(not piece.color, square))
                defenders = len(board.attackers(piece.color, square))
                if piece.color == False: # Case for black's attack/defense strength
                    if attackers > defenders:
                        piece_value = piece_values[piece.piece_type]
                        attackers_score += piece_value* (attackers-defenders)
                else: # Case for white's attack/defense strength
                    if attackers > defenders:
                        piece_value = piece_values[piece.piece_type]
                        # convention flipped here. Consider hung piece with no defenders. This is an advantage for black, so -
                        attackers_score -= piece_value* (attackers-defenders) 
        return attackers_score

    def king_threat_score(self, board):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        king_threat_score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                if board.is_pinned(piece.color, square):
                    if piece.color == True: # If white is pinned, black advantage
                        king_threat_score -= piece_values[piece.piece_type]
                    else:
                        king_threat_score += piece_values[piece.piece_type]
        return king_threat_score

def main():
    # odd depths end back on white's turn
    args = parse_arguments()
    depth = args.depth
    num_lines = args.num_lines
    pgn = args.write_pgn
    game = True

    write_intro()
    print(f'You are playing with a depth of {depth} with {num_lines} lines.\n'
          f'This evaluates a maximum of {num_lines**depth} positions per move.')

    # Can provide an FEN here to set a starting position. Default to standard for now

    # Note, can print pgn for a real analysis engine via print(game.from_board(board))

    board = chess.Board()
    print_board(board)
    while game:
        # Calculate legal moves for the pieces
        get_human_move(board)
        print_board(board)
        
        if board.is_checkmate() == False and board.is_stalemate() == False:
            stop_event = threading.Event()
            MCE = MCEngine(board, depth = depth, num_lines = num_lines, global_moves=board.fullmove_number)
            thinking_thread = threading.Thread(target=thinking_animation, args=(stop_event,))
            thinking_thread.start()
            MCE.line_generator()
            stop_event.set()
            thinking_thread.join()
            print_board(board)
            if board.is_checkmate():
                print('Black wins by checkmate!')
                game = False
            if board.is_stalemate():
                print('White is stalemated.')
                game = False
        elif board.is_checkmate():
            print('White wins by checkmate!')
            game = False
        elif board.is_stalemate():
            print('Black is stalemated.')
            game = False
    
    print('\nThanks for playing!')
    if pgn == True:
        utc_time = datetime.now(timezone.utc)
        formatted_datetime = utc_time.strftime("%d%m%Y-%H:%M")
        game = chess.pgn.Game().from_board(board)
        # game.from_board(board)
        game.headers["Event"] = f"MC Chess Game With a Depth {depth} and {num_lines} lines"
        print(game, file=open(f'./MCChess_Game_{formatted_datetime}UTC.txt', 'w'), end='\n\n')

if __name__ == "__main__":
    main()