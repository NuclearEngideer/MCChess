import chess
import chess.pgn
import re
import random
import pprint

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
    board_string = ''
    for line in board.unicode().split('\n'):
        if line:
            board_string +=f'{rank} ' + line + '\n'
            rank -= 1
    board_string += '  A B C D E F G H'
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


    def start_line_generator(self):
        LGOS = []
        #TODO set this test to >= 0 so the generator can play a full move ahead
        if self.depth > 0:
            for line in range(self.num_lines):
                print(f'Initializing Line Generator for line {line} at move {self.board.fullmove_number} for color {self.board.turn}')
                LGOS.append(self.LineGenerator(self, self.board.fullmove_number+line))
        else:
            print('reached depth')
        for LGO in LGOS:
            LGO.move_at_depth()

    class LineGenerator():
        def __init__(self, calling_mce, line_number):
            self.mce = calling_mce
            self.board = self.mce.board
            self.line_number = line_number
            self.depth = 0
    
        def initialize_prng(self):
            board_map = self.mce.board.piece_map()
            seed = 0
            for key, value in board_map.items():
                match value.symbol():
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
            seed += self.board.fullmove_number * self.line_number
            random.seed(seed)

        def random_move(self):
            random_move_index = random.randrange(0, self.board.legal_moves.count()-1)
            legal_moves = [move for move in self.board.legal_moves]
            selected_move = legal_moves[random_move_index]
            print(f'{selected_move}')
            # make selected_move
            self.board.push(selected_move)

        def move_at_depth(self):
            self.initialize_prng()
            self.random_move()
            self.depth = self.mce.stop_move_number - self.board.fullmove_number

            print(f'{self.depth}')
            print(self.board.unicode())
            MCEI = MCEngine(self.board, self.depth, self.mce.num_lines, self.board.fullmove_number)
            MCEI.start_line_generator()


    # initialize PRNG by board position (as square index * piece value) + (move count * line number)
    # we do this for reproducability while trying to avoid duplicates, maybe - arbitrary method currently
    # This isn't a great prng because the engine will probably always play the same move in a given position 
    # with the same depth and line number(s)

    def initialize_prng(self):
        board_map = self.board.piece_map()
        seed = 0
        for key, value in board_map.items():
            match value.symbol():
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
        seed += self.board.fullmove_number * self.line_number
        print(seed)
        random.seed(seed)
    
    def random_move(self):
        # Generate UCI string(s) for all legal moves
        # board_map = self.board.piece_map()
        # turn_pieces = []
        # for key in board_map.keys():
        #     if self.board.color_at(key) == self.board.turn:
        #         turn_pieces.append(key)
        # uci_strings = []
        # for piece in turn_pieces:
        #     for move in self.board.legal_moves:
        random_move_index = random.randrange(0, self.board.legal_moves.count()-1)
        legal_moves = [move for move in self.board.legal_moves]
        selected_move = legal_moves[random_move_index]
        self.board.push(selected_move)

    def is_good_position(self):
        # Want to check how good each positioin is
        # Count the attackers on a piece and if other pieces are defending it?
        pass

class LineGenerator():
    def __init__(self, board, stop_move_number, line_number):
        self.board = board
        self.line_number = line_number
        self.move_number = self.board.fullmove_number
        self.depth = stop_move_number-self.move_number
    
    def initialize_prng(self):
        board_map = self.board.piece_map()
        seed = 0
        for key, value in board_map.items():
            match value.symbol():
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
        seed += self.board.fullmove_number * self.line_number
        random.seed(seed)

    def random_move(self):
        random_move_index = random.randrange(0, self.board.legal_moves.count()-1)
        legal_moves = [move for move in self.board.legal_moves]
        selected_move = legal_moves[random_move_index]
        # return selected_move
        self.board.push(selected_move)
    
    def move_at_depth(self):
        self.initialize_prng()
        self.random_move()
        MCEngine(self.board, self.depth, self.lines)




def main():
    depth = 1
    num_lines = 2
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
        
        MCE = MCEngine(board, depth = depth, num_lines = num_lines, global_moves=board.fullmove_number)
        MCE.start_line_generator()

        # for line in range(num_lines):
        #     MCEngine(board, depth = depth, sub_lines=sub_lines, line_number=line, global_moves=board.fullmove_number)
            # Each of these will have to return 1 move option for the opposing color
            # here in main we will evaluate the move based on the returned move option and line strength of the best move line
        print_board(board)
        pass


if __name__ == "__main__":
    main()