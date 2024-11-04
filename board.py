# Class for the board
from pieces.pawn import pawn
from pieces.rook import rook
from pieces.knight import knight
from pieces.bishop import bishop
from pieces.queen import queen
from pieces.king import king
import colorama

class board():
    def __init__(self, side):
        self.coordinates = self.setup_coordinates()
        self.pieces=[]
        self.starting_position()
        self.side = side
        self.draw_board()

    def setup_coordinates(self):
        ranks = [1,2,3,4,5,6,7,8]
        files = ['A','B','C','D','E','F','G','H']
        coordinates = []
        for file in files:
            for rank in ranks:
                coordinates.append((file, rank))
        return coordinates

    def starting_position(self):
        for coordinate in self.coordinates:
            # Setup white pieces first
            if coordinate[1] == 2:
                self.pieces.append(pawn(position=coordinate, color='W'))
            if coordinate == ('C', 1) or coordinate == ('F', 1):
                self.pieces.append(bishop(position=coordinate, color='W'))
            if coordinate == ('B', 1) or coordinate == ('G', 1):
                self.pieces.append(knight(position=coordinate, color='W'))
            if coordinate == ('A', 1) or coordinate == ('H', 1):
                self.pieces.append(rook(position=coordinate, color='W'))
            if coordinate == ('D', 1):
                self.pieces.append(queen(position=coordinate, color='W'))
            if coordinate == ('E', 1):
                self.pieces.append(king(position=coordinate, color='W'))
            # Now do black pieces
            if coordinate[1] == 7:
                self.pieces.append(pawn(position=coordinate, color='W'))
            if coordinate == ('C', 8) or coordinate == ('F', 8):
                self.pieces.append(bishop(position=coordinate, color='W'))
            if coordinate == ('B', 8) or coordinate == ('G', 8):
                self.pieces.append(knight(position=coordinate, color='W'))
            if coordinate == ('A', 8) or coordinate == ('H', 8):
                self.pieces.append(rook(position=coordinate, color='W'))
            if coordinate == ('D', 8):
                self.pieces.append(queen(position=coordinate, color='W'))
            if coordinate == ('E', 8):
                self.pieces.append(king(position=coordinate, color='W'))
            
    def draw_board(self):
        ws = '0x25A1'
        bs = '0x25A0'
        template = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
        board_layout = {}
        for coordinate in self.coordinates:
            
        if self.side == 'B':
            order = self.coordinates
            ranks = [1,2,3,4,5,6,7,8]
        elif self.side == 'W':
            order = self.coordinates.reverse()
            ranks = [8,7,6,5,4,3,2,1]
        for coordinate in order:
            for piece in self.pieces:
                if piece.position == coordinate:
                    pass

    def position(self):
        pass

# I think what I'd like to do is read the position of all the live pieces
# And then translate that into the board that will be drawn (maybe)
# to the terminal.
# This allows all pieces to know where they are all the time, which will be useful for the MC portion
# I'll need to figure out how to set up threats on the board? Maybe define threats in each piece class
# Then loop through all the pieces and collect threatened squares as a list of dictionaries, 
# then combine like-keys to determine "goodness" of a particular square.
# Pop dead pieces from pieces list 