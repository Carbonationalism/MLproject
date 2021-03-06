from __future__ import print_function
import sys
from Game import Game
import chess
import numpy as np
import pickle
import re
eps=1e-6


f = lambda x: x.group()[0] + str(9 - int(x.group()[1]))
def mirrored_move(move):
    return re.sub('[e-h]\d', f, move)

class HalfchessGame(Game):
    """
    Half chess game described at https://chessvariants.com/small.dir/halfchess.html
    """
    def __init__(self):
        self.loadActions()

    def getInitBoard(self):
        return chess.Board('4rkqr/4nbbn/8/8/8/8/4NBBN/4RKQR w - - 0 1')

    def getBoardSize(self):
        return (8,4)

    def loadActions(self):
        #with open('python-chess/large_moveset.pickle', 'rb') as file:
        #with open('python-chess/med_moveset.pickle', 'rb') as file:
        #with open('small_moveset.pickle', 'rb') as file:
        with open('forward_moveset.pickle', 'rb') as file:
            self.moveset = pickle.load(file)

    def getActionSize(self):
        #return len(self.moveset) // 2
        return 348

    def getNextState(self, board, player, action):
        """
        return the next board state after taking the action
        """
        
        move = self.moveset[action]
        if player < 0:
            move = mirrored_move(move)
        if len(move) == 3:
            board.push_san(move) # todo, ensure this works without 'x' and other stuff
        else:
            board.push_uci(move[-4:]) # push last 4 letters of UCI or LAN UCI
        # TODO: have to figure out player or -player thing
        return board, -player

    def getValidMoves(self, board, player):
        moves = np.zeros(self.getActionSize())
        valids = np.array([self.moveset[i] for i in list(board.legal_moves.to_uci())])
        moves[valids] = 1
        return moves

    def getGameEnded(self, board, player):
        over = board.is_game_over()
        if not over:
            return 0
        result = board.result()
        if result == '1-0':
            return player
        elif result == '0-1':
            return -player
        else: # draw, return small nonzero
            return eps
        

    def getCanonicalForm(self, board, player):
        # flip board to white
        if board.turn == chess.BLACK:
            return board.mirror()
        else:
            return board
        

    def getSymmetries(self, board, pi):
        # TODO: do we have any other symmetries in this setup? 
        # I don't think so, more research into how AlphaGo used symmetry needed
        return [(board, pi)]

    def stringRepresentation(self, board):
        ### TODO: take move counts off of the board_fen in __repr__
        #return ' '.join(board.fen().split()[:-4])
        # board_fen doesn't contain any turn information and should only be used with canonical board
        return board.board_fen()

