# Class for knight

class knight():

    def __init__(self, position, color):
        self.color = color
        self.icon = 'N'
        self.position = position # A tuple
        self.legal_moves = []
        self.first_move = True
        self.value = 3
    
    def allowed_moves(self):
        single_move_forward = (self.position[0], self.position[1]+1)
        # first move can be two spaces
        if self.first_move == True:
            double_move_forward = (self.position[0], self.position[1]+2)
            self.legal_moves.append(double_move_forward)
            self.legal_moves.append(single_move_forward)
        elif self.first_move == False:
            self.legal_moves.append(single_move_forward)
            # Need to read board to see if there is a piece that can be taken and add
            # To legal moves
            # Maybe board class should calculate the legal moves and the piece classes just
            # Contain the allowable moves and value of the pieces?
            # TODO: Implement en passant
