# this is our driver file. It will be responsible for handling user input and displaying the current GameState object.
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame as p
import ChessEngine


width = height = 512  #400 is another option, any bigger than 512 quality starts to diminish
dimension = 8 #dimension of a chess board are 8x8
sq_size = height // dimension 
max_fps = 15 #for animations later on
images = {}

#we load images only once because its a very heavy operation. if we choose to load more that that its going to lag for every move as we increase notation.
'''
initialize a global dict of images. This will be called exactly once in the main.
'''
def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ' ]
    for piece in pieces:
        images[piece] = p.transform.scale.image.load('images/' + piece + '.png'), (sq_size, sq_size)
    #note: we can acess an image by saying 'images[' ']   -insert whatever piece in empty str-
#the main driver for our code. This will handle user input and updating the graphics

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag varible for when a move is made
    
    load_images()
    running = True
    sq_selected = () #no square is selected, keep track of the last click of the user(tuple:(row,col))
    player_clicks = [] #keep track of player clicks (tow tuples: [(6, 4), (4, 4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.mousebuttondown:
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
                            sq_selected = ()#reset user clicks
                            player_clicks = []
                    if not move_made:
                        player_clicks = [sq_selected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undo_move()
                    move_made = True
                    
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

                
        draw_GameState(screen,gs)
        clock.tick(max_fps)
        p.display.flip()

#reponsible for all the graphics within a current game state

def draw_GameState(screen, gs):
    draw_board(screen) #draws squares on the board
    #allows adding in piece highlighting or move suggestion (later)
    draw_pieces(screen, gs.board) #draws pieces on top of those squares


#this draws the squares on the board. can be addapted for color. board must be done first. Top left square is always light 
def draw_board(screen):
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
                screen.blit(images[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))



if __name__ == "__main__":
    main()

