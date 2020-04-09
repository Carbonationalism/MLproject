#!usr/bin/env python3

import pickle
import sys
sys.path.append('./alpha-zero-general/python-chess')
import chess

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
	for square in chess.SQUARES_180_HALF:
		board._set_piece_at(square, piece, chess.WHITE)
		for move in board.legal_moves.to_lanuci():
			moves_large[move] = i
			moves_large[i] = move
			i += 1
		board._clear_board()

moves_med = {}
j = 0
board = chess.Board(None)
for square in chess.SQUARES_180_HALF:
	board._set_piece_at(square, chess.QUEEN, chess.WHITE)
	for move in board.legal_moves.to_uci():
		moves_med[move] = j
		moves_med[j] = move
		j += 1
	board._clear_board()
	board._set_piece_at(square, chess.KNIGHT, chess.WHITE)
	for move in board.legal_moves.to_uci():
		moves_med[move] = j
		moves_med[j] = move
		j += 1
	board._clear_board()

moves_small = {}
board = chess.Board(None)
k = 0
for square in chess.SQUARES_180_HALF:
	square_name = chess.SQUARE_NAMES[square]
	for piece in chess.PIECE_TYPES[1:]:
		piece_symb = chess.PIECE_SYMBOLS[piece].upper()
		pan = piece_symb + square_name
		moves_small[pan] = k
		moves_small[i] = pan
		k += 1

# just curious
print(len(moves_large) // 2)
print(len(moves_med) // 2)
print(len(moves_small) // 2) 

with open('large_moveset.pickle', 'wb') as file:
	pickle.dump(moves_large, file)
with open('med_moveset.pickle', 'wb') as file:
	pickle.dump(moves_med, file)
with open('small_moveset.pickle', 'wb') as file:
	pickle.dump(moves_small, file)
		
		


	
