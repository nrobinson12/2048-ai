# file to store utilities that are helpful across all files

# gb = GameBoard
def print_board(gb):
    for i in range(4):
        for j in range(4):
            print("%6d  " % gb.grid[i][j], end="")
        print("")
    print("")
