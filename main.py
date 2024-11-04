# main module for mcchess
from board import board
from pieces.pawn import pawn
from pieces.rook import rook
from pieces.knight import knight
from pieces.bishop import bishop
from pieces.queen import queen
from pieces.king import king

def main():
    board(side='B')

if __name__ == '__main__':
    main()