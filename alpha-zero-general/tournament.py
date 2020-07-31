import sys
sys.path.append('python-chess/')
sys.path.append('python-chess/pytorch/')
import chess
import Arena
from MCTS import MCTS
from HalfchessGame import HalfchessGame

from HalfchessPlayers import RandomPlayer
from NNet import NNetWrapper as NNet

import numpy as np
from utils import *
import random

g = HalfchessGame()

filepath = 'full_run/'
det_pol = False
savefile = 'tourney_results.txt'
num_tourneys = 30
num_games = 2

nets = [1, 3, 14, 29, 48, 70, 98]
#nets = [1,14,98]
victories = {}
runner_up = {}

rp = RandomPlayer(g).play
victories[rp] = [0, 0]
runner_up[rp] = [0, 0]

playerpool = [rp]
args = dotdict({'numMCTSSims': 20, 'cpuct': 1.0, 'dirichlet': 0.05})

for i in nets:
    nn = NNet(g)
    nn.load_checkpoint(filepath, 'checkpoint_%d.pth.tar'%i)
    mcts = MCTS(g, nn, args)
    def stochastic(x):
        pi = mcts.getActionProb(x, temp=1)
        return np.random.choice(len(pi), p=pi)
    def deterministic(x):
        return np.argmax(mcts.getActionProb(x, temp=0))
    nnp = deterministic if det_pol else stochastic
    victories[nnp] = [i, 0]
    runner_up[nnp] = [i, 0]
    playerpool.append(nnp)


for it in range(num_tourneys):
    print('Tournament %d'%it)
    print('-------------')
    next_round = playerpool.copy()
    round_count = 0
    while len(next_round) > 1:
        print('Round %d'%round_count)
        round_count += 1
        championship = False
        this_round = next_round
        if len(this_round) == 2:
            championship = True
        next_round = []
        while this_round:
            random.shuffle(this_round)
            p1 = this_round.pop()
            p2 = this_round.pop()
            print('player 1: iteration %d'%victories[p1][0])
            print('player 2: iteration %d'%victories[p2][0])
            
            settled = False
            while not settled:
                arena = Arena.Arena(p1, p2, g, display=str)
                result = arena.playGames(num_games, verbose=False)
                if result[0] > result[1]:
                    next_round.append(p1)
                    print(result)
                    settled = True
                    if championship:
                        runner_up[p2][1] += 1
                elif result[1] > result[0]:
                    next_round.append(p2)
                    print(result)
                    settled = True
                    if championship:
                        runner_up[p1][1] += 1
                else:
                    print(result)
                    print('Undecisive, playing again')
    winner = next_round.pop()
    print('The winner is iteration %d'%victories[winner][0])
    
    victories[winner][1] += 1

    print('saving to file')
    with open(savefile, 'w') as file:
        for key in victories.keys():
            file.write('Iteration %d \t %d victories %d second place finishes\n'%(victories[key][0], victories[key][1], runner_up[key][1]))
