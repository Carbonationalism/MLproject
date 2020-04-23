import numpy as np

class RandomPlayer():
	def __init__(self, game):
		self.game = game

	def play(self, board):
		valids = self.game.getValidMoves(board, 1)
		a = np.random.choice(np.nonzero(valids)[0])
		return a

class HumanPlayer():
	def __init__(self, game):
		self.game = game

	def play(self, board):
		valids = self.game.getValidMoves(board, 1)
		
		actions = [self.game.moveset[v] for v in np.nonzero(valids)[0]]

		print(actions)

		input_action = input().strip()

		return self.game.moveset[input_action]
