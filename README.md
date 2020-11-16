# 2048 AI

Forked from [Lesaun](https://github.com/Lesaun/2048-expectimax-ai), who created the board and the original Expectimax algorithm. They also got the GUI from [yangshun](https://github.com/yangshun/2048-python).

This is a project to investigate artificial intelligence strategies to play and beat the game 2048. The algorithms that this used are both Expectimax and Monte Carlo Tree Search.

## Usage

There are a few ways to run the algorithm:

```bash
python3 main_cli.py # output board state in terminal
python3 main_gui.py # use gui to visualize board state
python3 main_batch.py # silent, output results in log files
```

You can change the algorithm used (either Expectimax or MCTS) in any of the `main` files.

## Resources Used

- 2048 optimal algorithm discussion on [Stack Overflow](https://stackoverflow.com/questions/22342854/what-is-the-optimal-algorithm-for-the-game-2048)

## License
[MIT](https://choosealicense.com/licenses/mit/)