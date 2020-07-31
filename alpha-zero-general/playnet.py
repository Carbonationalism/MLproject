
import os
import sys
sys.path.append('python-chess/')
sys.path.append('python-chess/pytorch/')
sys.path.append('PySimpleGUI/')
import PySimpleGUI as sg
import chess
import copy
import pickle

from MCTS import MCTS
import HalfchessGame
from NNet import NNetWrapper as NNet
import numpy as np
from utils import *

nn_filepath = './pretrained_models/halfchess'
nn_filename = '100it.pth.tar'
cpuct = 1.0
numMCTSSims = 50
human = 1 # 1 to play as white, -1 as black
temp = 1

with open('forward_moveset.pickle', 'rb') as file:
	moveset = pickle.load(file)

CHESS_PATH = './PySimpleGUI/Chess_files/'  # path to the chess pieces

BLANK = 0  # piece names
KNIGHTB = 2
BISHOPB = 3
ROOKB = 4
KINGB = 5
QUEENB = 6
KNIGHTW = 8
BISHOPW = 9
ROOKW = 10
KINGW = 11
QUEENW = 12

initial_board = [[ROOKB, QUEENB, KINGB, ROOKB],
                 [KNIGHTB, BISHOPB, BISHOPB, KNIGHTB],
                 [BLANK, ] * 4,
                 [BLANK, ] * 4,
                 [BLANK, ] * 4,
                 [BLANK, ] * 4,
                 [KNIGHTW, BISHOPW, BISHOPW, KNIGHTW],
                 [ROOKW, QUEENW, KINGW, ROOKW]]

blank = os.path.join(CHESS_PATH, 'blank.png')
bishopB = os.path.join(CHESS_PATH, 'bishopb.png')
bishopW = os.path.join(CHESS_PATH, 'bishopw.png')
knightB = os.path.join(CHESS_PATH, 'knightb.png')
knightW = os.path.join(CHESS_PATH, 'knightw.png')
rookB = os.path.join(CHESS_PATH, 'rookb.png')
rookW = os.path.join(CHESS_PATH, 'rookw.png')
queenB = os.path.join(CHESS_PATH, 'queenb.png')
queenW = os.path.join(CHESS_PATH, 'queenw.png')
kingB = os.path.join(CHESS_PATH, 'kingb.png')
kingW = os.path.join(CHESS_PATH, 'kingw.png')

images = {BISHOPB: bishopB, BISHOPW: bishopW, KNIGHTB: knightB, KNIGHTW: knightW,
          ROOKB: rookB, ROOKW: rookW, KINGB: kingB, KINGW: kingW, QUEENB: queenB, QUEENW: queenW, BLANK: blank}




def render_square(image, key, location):
    if (location[0] + location[1]) % 2:
        color = '#B58863'
    else:
        color = '#F0D9B5'
    return sg.RButton('', image_filename=image, size=(1, 1), button_color=('white', color), pad=(0, 0), key=key)


def redraw_board(window, board):
    for i in range(8):
        for j in range(4):
            color = '#B58863' if (i + j) % 2 else '#F0D9B5'
            piece_image = images[board[i][j]]
            elem = window.FindElement(key=(i, j))
            elem.Update(button_color=('white', color),
                        image_filename=piece_image, )


def PlayGame():
    menu_def = [['&File', ['&Do nothing', 'E&xit']],
                ['&Help', '&About...'], ]

    # sg.SetOptions(margins=(0,0))
    sg.ChangeLookAndFeel('GreenTan')
    # create initial board setup
    psg_board = copy.deepcopy(initial_board)
    # the main board display layout
    board_layout = [[sg.T('     ')] + [sg.T('{}'.format(a), pad=((23, 27), 0), font='Any 13') for a in 'efgh']]
    # loop though board and create buttons with images
    for i in range(8):
        row = [sg.T(str(8 - i) + '   ', font='Any 13')]
        for j in range(4):
            piece_image = images[psg_board[i][j]]
            row.append(render_square(piece_image, key=(i, j), location=(i, j)))
        row.append(sg.T(str(8 - i) + '   ', font='Any 13'))
        board_layout.append(row)
    # add the labels across bottom of board
    board_layout.append([sg.T('     ')] + [sg.T('{}'.format(a), pad=((23, 27), 0), font='Any 13') for a in 'efgh'])

    # setup the controls on the right side of screen
    openings = (
        'Any', 'Defense', 'Attack', 'Trap', 'Gambit', 'Counter', 'Sicillian', 'English', 'French', 'Queen\'s openings',
        'King\'s Openings', 'Indian Openings')

    board_controls = [[sg.RButton('New Game', key='New Game'), sg.RButton('Draw')],
                      [sg.RButton('Resign Game'), sg.RButton('Set FEN')],
                      [sg.RButton('Player Odds'), sg.RButton('Training')],
                      [sg.Drop(openings), sg.Text('Opening/Style')],
                      [sg.CBox('Play As White', key='_white_')],
                      [sg.Text('Move List')],
                      [sg.Multiline([], do_not_clear=True, autoscroll=True, size=(15, 10), key='_movelist_')],
                      ]

    # layouts for the tabs
    controls_layout = [[sg.Text('Performance Parameters', font='_ 20')],
                       [sg.T('Put stuff like AI engine tuning parms on this tab')]]

    statistics_layout = [[sg.Text('Statistics', font=('_ 20'))],
                         [sg.T('Game statistics go here?')]]

    board_tab = [[sg.Column(board_layout)]]

    # the main window layout
    layout = [[sg.Menu(menu_def, tearoff=False)],
              [sg.TabGroup([[sg.Tab('Board', board_tab),
                             sg.Tab('Controls', controls_layout),
                             sg.Tab('Statistics', statistics_layout)]], title_color='red'),
               sg.Column(board_controls)],
              [sg.Text('Click anywhere on board for next move', font='_ 14')]]

    window = sg.Window('Chess',
                       default_button_element_size=(12, 1),
                       auto_size_buttons=False,
                       icon='kingb.ico').Layout(layout)

    g = HalfchessGame.HalfchessGame()
    nn = NNet(g)
    nn.load_checkpoint(nn_filepath, nn_filename)
    args = dotdict({'numMCTSSims': numMCTSSims, 'cpuct': cpuct})
    mcts = MCTS(g, nn, args)
    nnp = lambda x: np.argmax(mcts.getActionProb(x, temp=temp))

    board = g.getInitBoard()
    move_count = curPlayer = 1
    move_state = move_from = move_to = 0
    # ---===--- Loop taking in user input --- #
    while g.getGameEnded(board, curPlayer) == 0:

	    canonicalBoard = g.getCanonicalForm(board, curPlayer)

	    if curPlayer == human:
	        # human_player(board)
	        move_state = 0
	        while True:
	            button, value = window.Read()
	            if button in (None, 'Exit'):
	                exit()
	            if button == 'New Game':
	                sg.Popup('You have to restart the program to start a new game... sorry....')
	                break
	                psg_board = copy.deepcopy(initial_board)
	                redraw_board(window, psg_board)
	                move_state = 0
	                break
	            
	            if type(button) is tuple:
	                if move_state == 0:
	                    move_from = button
	                    row, col = move_from
	                    piece = psg_board[row][col]  # get the move-from piece
	                    button_square = window.FindElement(key=(row, col))
	                    button_square.Update(button_color=('white', 'red'))
	                    move_state = 1
	                elif move_state == 1:
	                    move_to = button
	                    row, col = move_to
	                    if move_to == move_from:  # cancelled move
	                        color = '#B58863' if (row + col) % 2 else '#F0D9B5'
	                        button_square.Update(button_color=('white', color))
	                        move_state = 0
	                        continue

	                    picked_move = '{}{}{}{}'.format('efgh'[move_from[1]], 8 - move_from[0],
	                                                    'efgh'[move_to[1]], 8 - move_to[0])

	                    action = moveset[picked_move]

	                    valids = g.getValidMoves(canonicalBoard,1)

	                    if valids[action] != 0:
	                        board, curPlayer = g.getNextState(board, curPlayer, action)
	                    else:
	                        print('Illegal move')
	                        move_state = 0
	                        color = '#B58863' if (move_from[0] + move_from[1]) % 2 else '#F0D9B5'
	                        button_square.Update(button_color=('white', color))
	                        continue

	                    psg_board[move_from[0]][move_from[1]] = BLANK  # place blank where piece was
	                    psg_board[row][col] = piece  # place piece in the move-to square
	                    redraw_board(window, psg_board)
	                    move_count += 1

	                    window.FindElement('_movelist_').Update(picked_move + '\n', append=True)

	                    break
	    else:

	        best_move = nnp(canonicalBoard)
	        move_str = moveset[best_move]

	        if curPlayer == -1:
	        	move_str = HalfchessGame.mirrored_move(move_str)

	        from_col = ord(move_str[0]) - ord('e')
	        from_row = 8 - int(move_str[1])
	        to_col = ord(move_str[2]) - ord('e')
	        to_row = 8 - int(move_str[3])

	        window.FindElement('_movelist_').Update(move_str + '\n', append=True)

	        piece = psg_board[from_row][from_col]
	        psg_board[from_row][from_col] = BLANK
	        psg_board[to_row][to_col] = piece
	        redraw_board(window, psg_board)

	        board, curPlayer = g.getNextState(board, curPlayer, best_move)
	        move_count += 1
    sg.Popup('Game over!', 'Thank you for playing')


PlayGame()
