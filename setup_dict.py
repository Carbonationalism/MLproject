#!usr/bin/env python3

import pickle
import sys
sys.path.append('./alpha-zero-general/python-chess')
import chess
import re

f = lambda x : x.group()[0] + str(9 - int(x.group()[1]))
def mirror(move):
	return re.sub('[e-h]\d', f, move)

"""
	First we enumerate all moves that are distinct by 
	the starting square, the target square, and the piece
	for a total of 1260 moves
"""
moves_large = {}
i = 0
# empty board
board = chess.Board(None)
# for knight, bishop, rook, queen, king
for piece in chess.PIECE_TYPES[1:]:
	# only go through a quarter of the squares from white's perspective, then add mirrored moves to back
	for square in chess.SQUARES_180_HALF:

		board._set_piece_at(square, piece, chess.WHITE)

		for move in board.legal_moves.to_lanuci():
			if move not in moves_large:
				moves_large[move] = i
				moves_large[i] = move

				mirrored = mirror(move)
				moves_large[mirrored] = 1259 - i
				moves_large[1259 - i] = mirrored
				i += 1
		board._clear_board()

moves_med = {}
j = 0 
board = chess.Board(None)
for square in chess.SQUARES_180_HALF:
	board._set_piece_at(square, chess.QUEEN, chess.WHITE)
	for move in board.legal_moves.to_uci():
		if move not in moves_med:
			moves_med[move] = j
			moves_med[j] = move

			mirrored = mirror(move)
			moves_med[mirrored] = 599 - j
			moves_med[599 - j] = mirrored
			j += 1

	board._clear_board()
	board._set_piece_at(square, chess.KNIGHT, chess.WHITE)
	for move in board.legal_moves.to_uci():
		if move not in moves_med:
			moves_med[move] = j
			moves_med[j] = move
			mirrored = mirror(move)
			moves_med[mirrored] = 599 - j
			moves_med[599 - j] = mirrored
			j += 1

	board._clear_board()

forward_moves = {}
board = chess.Board(None)
j = 0
for square in chess.SQUARES_180_HALF:
	board._set_piece_at(square, chess.QUEEN, chess.WHITE)
	for move in board.legal_moves.to_uci():
		forward_moves[move] = j
		forward_moves[j] = move

                morrored = mirror(move)
                if mirror not in forward_moves:
                        forward_moves[mirror] = j
		j += 1

	board._clear_board()
	board._set_piece_at(square, chess.KNIGHT, chess.WHITE)
	for move in board.legal_moves.to_uci():
		forward_moves[move] = j
		forward_moves[j] = move

                mirrored = mirror(move)
                if mirror not in forward_moves:
                        forward_moves[mirror] = j
		j += 1

	board._clear_board()
print('forward moveset size %d'%j)

#TODO: if we use this, need to fix some double counting somewhere
moves_small = {}
board = chess.Board(None)
k = 0
for square in chess.SQUARES_180_HALF:
	square_name = chess.SQUARE_NAMES[square]
	for piece in chess.PIECE_TYPES[1:]:
		piece_symb = chess.PIECE_SYMBOLS[piece].upper()
		pan = piece_symb + square_name
		mirror_pan = mirror(pan)

		if pan not in moves_small:
			moves_small[pan] = k
			moves_small[k] = pan

			moves_small[mirror_pan] = 79 - k
			moves_small[79 - k] = mirror_pan
			k += 1

# just curious
print(len(moves_large) // 2)
print(len(moves_med) // 2)
print(len(moves_small) // 2) 
print(len(forward_moves) // 2)

for n in range(1260):
	assert(moves_large[n] == mirror(moves_large[1259 - n]))

with open('large_moveset.pickle', 'wb') as file:
	pickle.dump(moves_large, file)
with open('med_moveset.pickle', 'wb') as file:
	pickle.dump(moves_med, file)
with open('small_moveset.pickle', 'wb') as file:
	pickle.dump(moves_small, file)
with open('forward_moveset.pickle', 'wb') as file:
	pickle.dump(forward_moves, file)
		

	
