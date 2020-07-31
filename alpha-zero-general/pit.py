import sys
sys.path.append('python-chess/')
sys.path.append('python-chess/pytorch/')
import chess
import Arena
from MCTS import MCTS
#from othello.OthelloGame import OthelloGame
#from othello.OthelloPlayers import *
#from othello.pytorch.NNet import NNetWrapper as NNet
from HalfchessGame import HalfchessGame
from HalfchessPlayers import *
from NNet import NNetWrapper as NNet


import numpy as np
from utils import *

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

human_vs_cpu = True

g = HalfchessGame()

# all players
rp = RandomPlayer(g).play
# gp = GreedyOthelloPlayer(g).play
hp = HumanPlayer(g).play

# nnet player
nn = NNet(g)
#nn.load_checkpoint('./temp/','best.pth.tar')
nn.load_checkpoint('./pretrained_models/halfchess', '43it.pth.tar')
args = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
mcts = MCTS(g, nn, args)
nnp = lambda x: np.argmax(mcts.getActionProb(x, temp=1))


if human_vs_cpu:
    player1 = hp
else:
    n2 = NNet(g)
    n2.load_checkpoint('./pretrained_models/halfchess/', '26it_fixed_logic.pth.tar')
    args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
    mcts2 = MCTS(g, n2, args2)
    n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

#     player2 = n2p  # Player 2 is neural network if it's cpu vs cpu.

arena = Arena.Arena(hp, nnp, g, display=str)

print(arena.playGames(2, verbose=True))
