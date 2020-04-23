from Coach import Coach
import sys
sys.path.append('python-chess/')
sys.path.append('python-chess/pytorch/')
# from othello.OthelloGame import OthelloGame as Game
# from othello.pytorch.NNet import NNetWrapper as nn
from HalfchessGame import HalfchessGame as Game
from NNet import NNetWrapper as HalfchessNNet
from utils import *


args = dotdict({
    'numIters': 100,
    'numEps': 100,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 25,        #
    'updateThreshold': 0.6,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 300000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 25,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 40,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    #'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'load_folder_file': ('temp/','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

    'dirichlet': 0.03,
})

if __name__ == "__main__":
    g = Game()
    nnet = HalfchessNNet(g)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
