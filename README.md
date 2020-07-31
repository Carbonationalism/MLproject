# ML Project

We used a scaled down alpha-zero approach implemented in python from [suragnair/alpha-zero-general](https://github.com/suragnair/alpha-zero-general) to train a chess bot on a simple chess variant we call halfchess. This layout of this variant is depicted [here](https://www.chessvariants.com/small.dir/halfchess.html), though we also enforce an additional restriction that pieces can only move forward or laterally, not backwards. This greatly simplifies the training process (making it somewhat feasible for a non-distributed alpha zero approach implemented entirely in python) by reducing the game length and total action space. 

## Credits 

### Team members:
Joseph Green and James Lee

### Repositories used:
* [alpha-zero-general](https://github.com/suragnair/alpha-zero-general) - the main framework we adapted to train a halfchess network
* [python-chess](https://github.com/niklasf/python-chess) - the underlying chess engine we adapted to fit our halfchess logic
* [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI) - we use this for a GUI to play the network with