import math
import numpy as np
EPS = 1e-8
import sys
import resource
sys.path.append('python-chess')
from chess import Board

class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}       # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}       # stores #times edge s,a was visited
        self.Ns = {}        # stores #times board s was visited
        self.Ps = {}        # stores initial policy (returned by neural net)

        self.Es = {}        # stores game.getGameEnded ended for board s
        self.Vs = {}        # stores game.getValidMoves for board s

        self.root = game.stringRepresentation(game.getInitBoard())
        self.noise_added = False

        resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))
        sys.setrecursionlimit(10**6)

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        if temp == 0:
            self.noise_added = True #workaround for deterministic behavior in self play eval 
    ### MODIFICATION: store the current board state here so subsequent MCTS don't use the same one
    # TODO: this board_fen doesn't have a turn marker, get one that does
        fen = canonicalBoard.fen()
        for i in range(self.args.numMCTSSims):
            self.search(Board(fen))
    ###

        s = self.game.stringRepresentation(canonicalBoard)
        counts = np.array([self.Nsa[(s,a)] if (s,a) in self.Nsa else 0 for a in range(self.game.getActionSize())])


        if temp==0:
            return (np.argmax(counts) == np.arange(len(counts))).astype(float)
        #    bestA = np.argmax(counts)
        #    probs = [0]*len(counts)
        #    probs[bestA]=1
        #    return probs

        # TODO: vectorize this with numpy since we've got a large action space
        return np.float_power(counts, (1./temp)) / np.sum(counts)
        #counts = [x**(1./temp) for x in counts]
        #counts_sum = float(sum(counts))
        #probs = [x/counts_sum for x in counts]
        #return probs


    def search(self, canonicalBoard):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """

        s = self.game.stringRepresentation(canonicalBoard)

### MODIFICATION: can't store things like Es since ending depends on move count and we want state indep. of move count
        result = self.game.getGameEnded(canonicalBoard, 1)
        if result != 0:
            if result not in (-1, 1):
                result = 0
            return -result
###

        # if s not in self.Es:
        #     self.Es[s] = self.game.getGameEnded(canonicalBoard, 1)
        # if self.Es[s]!=0:
        #     # terminal node
        #     return -self.Es[s]


        if s not in self.Ps:
            # leaf node
            self.Ps[s], v = self.nnet.predict(canonicalBoard.toarray()) ### modified to convert the chess board to array
            valids = self.game.getValidMoves(canonicalBoard, 1)
            self.Ps[s] = self.Ps[s]*valids      # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s    # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable
                
                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.   
                print("All valid moves were masked, do workaround.")
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        if s == self.root and not self.noise_added:
            self.Ps[s] = 0.75 * self.Ps[s] + 0.25 * np.random.dirichlet(np.ones_like(self.Ps[s]) * self.args.dirichlet)
            self.noise_added = True # a bit scared I might add extra noise on successive searches from root
        
        ### TODO: it's validity checking by storing valid moves here 
        # this doesn't really work since the stringRepresentation we're using is player-agnostic
        # we can fix this by A: calling getValidMoves each time instead of storing them but thats slow
        # or B: changing stringRepresentation to be something like board_fen (this is probably the way to go)
        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        # for a in range(self.game.getActionSize()):
        #     if valids[a]:
        #         if (s,a) in self.Qsa:
        #             u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
        #         else:
        #             u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s] + EPS)     # Q = 0 ?

        #         if u > cur_best:
        #             cur_best = u
        #             best_act = a
### MODIFICATION: the above is slow
        for a in np.nonzero(valids)[0]:
            if (s,a) in self.Qsa:
                u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
            else:
                u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s] + EPS)     # Q = 0 ?

            if u > cur_best:
                cur_best = u
                best_act = a
###

        a = best_act
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)
        next_s = self.game.getCanonicalForm(next_s, next_player)

        v = self.search(next_s)

        if (s,a) in self.Qsa:
            self.Qsa[(s,a)] = (self.Nsa[(s,a)]*self.Qsa[(s,a)] + v)/(self.Nsa[(s,a)]+1)
            self.Nsa[(s,a)] += 1

        else:
            self.Qsa[(s,a)] = v
            self.Nsa[(s,a)] = 1

        self.Ns[s] += 1
        return -v
