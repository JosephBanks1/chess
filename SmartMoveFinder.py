import random
from typing import counter

piece_score = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}
checkmate = 1000
stalemate = 0
DEPTH = 2





#picks and returns a random move
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

#find the best move, min max w/o recursion
def find_best_move_min_max_no_recursion(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_min_max_score = checkmate
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()
        if gs.stalemate:
            opponent_max_score = stalemate
        elif gs.checkmate:
            opponent_max_score = -checkmate
        else:
            opponent_max_score = -checkmate
            for opponents_moves in opponents_moves:
                gs.make_move(opponents_moves)
                if gs.checkmate:
                    score = -turn_multiplier * checkmate
                elif gs.stalemate:
                    score = stalemate
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                    best_player_move = player_move
                gs.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move

#helper method to make first recursive call
def find_best_move(gs, valid_moves):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    #find_move_min_max(gs, valid_moves, DEPTH, gs.white_to_move)

#swap comment out on lines 60 and 61 to see prunning effects in counter

    # find_move_nega_max(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -checkmate, checkmate, 1 if gs.white_to_move else -1)
    print(counter)
    return next_move


def find_move_min_max(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return score_material(gs.board)
    
    if white_to_move:
        max_score = -checkmate
        for move in valid_moves:
            gs.make_move()
            next_move = gs.get_valid_moves()
            score = find_move_min_max(gs, next_move, depth -1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = checkmate
        for move in valid_moves:
            gs.make_move(move)
            score = find_move_min_max(gs, next_move, depth -1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move
        return max_score


def find_move_nega_max(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -checkmate
    for move in valid_moves:
        gs.make_move(move)
        next_move = gs.get_valid_moves()
        score = -find_move_nega_max(gs, next_move, depth -1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score


def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)


    #move ordering - implement later
    max_score = -checkmate
    for move in valid_moves:
        gs.make_move(move)
        next_move = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_move, depth -1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha: #pruning happens here
            alpha = max_score
        if alpha >= beta:
            break
    return max_score
#a positive score is gos for white, a nega score is good for black
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -checkmate#black wins
        else:
            return checkmate #white wins
    elif gs.stalemate:
        return stalemate

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score

#score the board based on material
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]


    return score

