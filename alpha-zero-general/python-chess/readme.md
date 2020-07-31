This folder contains the [python-chess](https://github.com/niklasf/python-chess) engine adapted for halfchess logic

Halfchess changes:
* Only forward or lateral moves are permitted
* As such, when both kings move past all of the opposite non-king pieces, stalemate is declared
* The board is cut in half
* No pawns