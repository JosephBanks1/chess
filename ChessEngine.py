# this class is responsible for storing all the info about the current state of a chess game. It will also be resposible for determining the valid moves at the current state. It will also keep a move log
# from os import truncate
# from tabnanny import check
# from turtle import back
# from numpy import true_divide


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
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves, 'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.moveLog = []
        self.white_to_move = True
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = () #coordinates for the square where en passant is possible
        self.current_castling_right = castle_rights(True, True, True, True)
        self.castle_rights_log = [castle_rights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs)]
        


    #Takes a move as a parameter and executes it (this will not work for castling,pawn promotion and en-pasant)
    def make_move(self, move):
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = "--"
        self.move_log.append(move) #log the move so we can undo it later
        self.white_to_move = not self.white_to_move #swap players
        #update the kings location if moved
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)
        
        #pawn promotion
        if move.is_pawn_promotion:
            promoted_piece = input("Promote to Q, R, B, or N:") #we can make this part of the ui later
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece

        #enpassant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--' #capturing the pawn

        #update enpassant possible var
        if move.piece_moved[1] == 'P' and abs(move.start_row - move. end_row) == 2: #only on 2 square pawn advances
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.enpassant_possible = ()

        #castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: #kingside castle move
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1] #moves the rook
                self.board[move.end_row][move.end_col+1] = '--' #erase old rook
            else: #queenside castle move
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col -2] #moves the rook
                self.board[move.end_row][move.end_col-2] = '--'


    #update casting rights - whenever it is a rook or a king move
        self.update_castle_rights(move)
        self.castle_rights_log.append(castle_rights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs))


    #undo the last mvoe
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move #switch turns back
            #update the kings position if moved
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)
            #undo enpassant 
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--' #leanve landing square black
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            #undo a 2 square pawn advance
            if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()
            #undo castling rights
            self.castle_rights_log.pop() #get rid of the new castle rights from the move we are undoing
            self.current_castling_right = self.castle_rights_log[-1] #set the current castle rights to the last one in the list
            #undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2: #kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else: #queenside
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'

    #update the castle rights given the move
    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved =='bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0: #left rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7: #right rook
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0: #left rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7: #right rook
                    self.current_castling_right.bks = False

    #all moves considering checks
    def get_valid_moves(self):
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = castle_rights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs)
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self. black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves = self.get_all_possible_moves() #to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] #check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] #enemy piece causeing the check
                valid_squares = [] #squares that pieces can move to
                #if knight, must capture knight or move king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1,8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) #check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: #once you get to pieces end checks
                            break
                #get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1): #go through backwards when you are removing from a list as iterating
                    if moves[i].piece_moved[1] != 'K': #move doesnt move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: #move doesnt block check or capture piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else: #not in check so all moves are fine
            moves = self.get_all_possible_moves()

        self.enpassant_possible = temp_enpassant_possible
        return moves # for now we will not worry about checks

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])
    
    #all moves without considering checks
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)#calls the appropriate move funciton based on piece
        return moves
    #get all the pawn moves for the pawn located at row, col, and add these moves to the list
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True 
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = 'b'
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = 'w'
        pawn_promotion = False

        if self.board[r + move_amount][c] == "--": #1 square move
            if not piece_pinned or pin_direction == (move_amount, 0):
                if r + move_amount == back_row: #if piece gets to back rank then it is a pawn promotion
                    pawn_promotion = True
                moves.append(Move((r, c), (r+ move_amount, c), self.board, pawn_promotion = pawn_promotion))
                if r == start_row and self.board[r+2 * move_amount][c] == "--": #2 square moves
                    moves.append(Move((r,c), (r+2 * move_amount, c), self.board))

        #captures
        if c-1 >= 0: #captures to the left
            if not piece_pinned or pin_direction == (move_amount, -1):            
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    if r + move_amount == back_row: # piece gets to bank rank them it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((r, c), (r+move_amount, c-1), self.board, pawn_promotion = pawn_promotion))
        
                if (r+move_amount, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+move_amount, c-1), self.board, enpassant = True))
        if c+1 <= 7: #captures to the right 
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r+move_amount][c + 1][0] == enemy_color:
                    if r + move_amount == back_row: #if piece gets to bank rank theen its a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((r, c), (r+move_amount, c+1), self.board, pawn_promotion = pawn_promotion))
                if (r+move_amount, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+move_amount, c+1), self.board, enpassant_move = True))
        
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move #switch to oppenets turn
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move #switch turns back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c: #square is under attack
                return True
        return False

    #get all the pawn moves for the rook located at row, col, and add these moves to the list
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #on board
                    end_piece = self.board[end_row][end_col]
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece + self.board[end_row][end_col]
                        if end_piece == '--': #empty space valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: #enemy piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break

    #get all the pawn moves for the rook located at row, col, and add these moves to the list
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #up-l, up-r, left-up, left-down, down-l, down-r, right-up, right-down
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row <8 and 0 <= end_col <8:
                end_piece = self.board[end_row][end_col]
                if not piece_pinned:
                    end_piece[0] != self.board[end_row][end_col]
                    if end_piece[0] != ally_color: #not an ammly piece (empty or enemy piece)
                        moves.append(Move((r, c), (end_row, end_col), self.board))



    #get all the pawn moves for the rook located at row, col, and add these moves to the list
    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins [i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #up, left, down, right
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8): #bishop can move a max of 7 squares
                end_row = r +d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col <8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--': #empthy space valid
                            moves.append(Move((r, c), end_row, end_col), self.board)
                        elif end_piece[0] == enemy_color: #enemy piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break


    #get all the pawn moves for the rook located at row, col, and add these moves to the list
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)


    #get all the pawn moves for the rook located at row, col, and add these moves to the list
    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col <8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: #not an ally piece (empty or enemy piece)
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    if ally_color == 'w':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)
        self.get_castle_moves(r, c, moves, ally_color)


    #generate all valid castle moves for the king at (r, c) and add them to the list of moves
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return #cant caslt while we are in check
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.get_kingside_castle_moves(r, c, moves, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.get_queenside_castle_moves(r, c, moves, moves)


    def get_kingside_castle_moves(self, r, c, moves, ally_color):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True ))
        

    def get_queenside_castle_moves(self, r, c, moves, ally_color):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3]:
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))


    #returns if the player is in check, a list of pins, and a list of checks

    def check_for_pins_and_checks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from 
        checks = [] #square where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () #reset possible pins
            for i in range(1, 8):
                end_row = start_row +d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece[0] = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == (): #1st allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        #5 possibilities here in this complex conditional
                        #1. orthogonally away from king and piece is a rook
                        #2. diagonally away from the king and the piece is a bishop
                        #3. 1 square away diagonally from king and piece is a pawn
                        #4. any direction and pieces is a queen
                        #5. any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'P' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == (): #no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else: #enemy piece not applying check:
                            break
                else:
                    break #off board
        #check for knight moves
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col <8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N': #enemy knight attacking king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

class castle_rights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self. bqs = bqs



class Move():
#maps keys to values
#key : values
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    col_is_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False, is_castle_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_catured = board[self.end_row][self.end_col]
        #pawn promotion stuff
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 8)
        #en passant stuff
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_catured = 'wP' if self.piece_moved == 'bP' else 'bP'
        #castle move
        self.is_castle_move = is_castle_move

        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        print(self.moveID)

#overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_Chess_Notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
