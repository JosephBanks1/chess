# this is our driver file. It will be responsible for handling user input and displaying the current GameState object.
import os
# from tkinter.tix import IMAGE
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame as p
import ChessEngine


width = height = 512  #400 is another option, any bigger than 512 quality starts to diminish
dimension = 8 #dimension of a chess board are 8x8
sq_size = height // dimension 
max_fps = 15 #for animations later on
IMAGE = {}

#we load IMAGE only once because its a very heavy operation. if we choose to load more that that its going to lag for every move as we increase notation.
'''
initialize a global dict of IMAGE. This will be called exactly once in the main.
'''
def load_IMAGE():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ' ]
    for piece in pieces:
        IMAGE[piece] = p.transform.scale.image.load('IMAGE/' + piece + '.png'), (sq_size, sq_size)
    #note: we can acess an image by saying 'IMAGE[' ']   -insert whatever piece in empty str-
#the main driver for our code. This will handle user input and updating the graphics

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag varible for when a move is made
    animate = False #flag vaible for when we should animate a move

    
    load_IMAGE()
    running = True
    sq_selected = () #no square is selected, keep track of the last click of the user(tuple:(row,col))
    player_clicks = [] #keep track of player clicks (tow tuples: [(6, 4), (4, 4)])
    gameover = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.mousebuttondown:
                if not gameover:
                    location = p.mouse.get_pos() #(x, y) location of mouse
                    col = location[0]//sq_size
                    row = location[1]//sq_size
                    if sq_selected == (row, col): #the user clicked the same square twice
                        sq_selected = () #deselected
                        player_clicks = [] #clear player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) #append for both 1st and 2nd clicks
                    if len(player_clicks) == 2: #after 2nd click
                        move = ChessEngine.move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notations())
                        for i in range(len(valid_moves)):
                            if move in valid_moves:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animtate = True
                                sq_selected = ()#reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undo_move()
                    move_made = True
                    animtate = False
                if e.key == p.K_r: #reset the board when 'r is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

                    
        if move_made:
            if animate:
              animate_move(gs.moveLog[-1], screen, gs.board,clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
                
        draw_GameState(screen,gs)

        if gs.checkmate:
            gameover = True
            if gs.white_to_move:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameover = True
            drawText(screen, 'Stalemate')

        clock.tick(max_fps)
        p.display.flip()


#highlight square selected and moves for pieces selected
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): #sqselected is a piece that can be moved
            #highlight selected square
            s= p.Surface((sq_size, sq_size))
            s.set_alpha(100) #transperancy value -> 0 trans; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*sq_size, r*sq_size))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*sq_size, move.endRow*sq_size))



#reponsible for all the graphics within a current game state

def draw_GameState(screen, gs, valid_moves, sq_selected):
    draw_board(screen) #draws squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board) #draws pieces on top of those squares


#this draws the squares on the board. can be addapted for color. board must be done first. Top left square is always light 
def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color('grey')]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*sq_size, sq_size, sq_size))
            

#will draw the pieces on the boardusing the current GameState.board
def draw_pieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGE[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

#aninmating a move

def animate_move(move, screen, board, clock):
    global colors
    coords = [] #list of coords that the animation will move through
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10 #frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR*frame/frame_count, move.start_col + dC*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*sq_size, move.end_row*sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.piece_captured != '--':
            screen.blit(IMAGE[move.piece_captured], end_square)
        #draw moving piece
        screen.blit(IMAGE[move.piece_moved], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60) 
    
def drawText(screen, text):
    font = p.font.SysFont('Helvetica', 32, True, False)
    text_object = font.render(text, 0, p.Color('Grey'))
    text_location = p.Rect(0, 0, width, height).move(width/2 - text_object.get_width()/2, height/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Red'))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()

