### Monte Carlo Chess ###

Use: `python3 mcengine.py [-n <number of lines> -d <depth>]`

This is a semi-deterministic monte carlo chess engine.
The engine relies on the `python-chess` package for low level chess operations like piece control, checkmates/checks, and legal moves.
The Monte Carlo portion of this engine spins up `number of lines`^`depth` total final positions then evaluates each position at the final depth with a hand-crafted positional goodness function.
There are many nuances that are not accounted for here both in the generation of lines and in the positional calculation.

Ideally, each line should cull itself after a partial depth if the position after some shallow number of moves is very bad. Surviving lines could continue to a greater depth and return a stronger move. This could be implemented but is currently not. 