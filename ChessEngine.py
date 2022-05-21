# this class is responsible for storing all the info about the current state of a chess game. It will also be resposible for determining the valid moves at the current state. It will also keep a move log



class GameState():
    def __init__(self):
        # board is 8x8 2d list, ea element of the list has 2 characters. The first char is the color, 'b' or 'w'. The second char is the type of the piece, 'K', 'Q', etc. and '--' represents and empty space with no piece.
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP',],
            ['--', '--', '--', '--', '--', '--', '--', '--',],
            ['--', '--', '--', '--', '--', '--', '--', '--',],
            ['--', '--', '--', '--', '--', '--', '--', '--',],
            ['--', '--', '--', '--', '--', '--', '--', '--',],
            ['--', '--', '--', '--', '--', '--', '--', '--',],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP',],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
 ]
        self.whiteToMove = True
        self.moveLog = []
#Takes a move as a parameter and executes it (this will not work for castling,pawn promotion and en-pasant)
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) #log the move so we can undo it later
        self.white_to_move = not self.white_to_move #swap players

#undo the last mvoe
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move #switch turns black

    #all moves considering checks
    def get_valid_moves(self):
        return self.get_all_possible_moves() # for now we will not worry about checks

    #all moves without considering checks
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.get_pawn_moves(r, c, moves)
                    elif piece == 'R':
                        self.get_rook_moves(r, c, moves)
        return moves


    #get all the pawn moves for the pawn located at row, col, and add these moves to the list
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move(r, c), (r-1, c), self.board)
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r,c), (r-2, c), self.board))
        if c-1 >= 0: #captures to the left
            if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                moves.append(Move((r-1, c-1), (r-1, c-1), self.board))
        if c+1 <= 7: #captures to the right 
            if self.board[r-1][c+1][0] == 'b':
                moves.append(Move((r-1, c+1), (r-1, c+1), self.board))
        

    #get all the pawn moves for the rook located at row, col, and add these moves to the list
    def get_rook_moves(self, r, c, moves):
        pass

class Move():
#maps keys to values
#key : values
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    col_is_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_catured = board[self.end_row][self.end_col]
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        print(self.moveID)

#overriding the equals method
    def __eq__(self, other):
        if isinstance(other, move):
            return self.moveID == other.moveID
        return False

    def get_Chess_Notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self,r, c):
        return self.cols_to_files[c] + self.rows_to_rans[r]
