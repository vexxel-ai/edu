# Reference: https://algo.monster/liteproblems/63
def unique_paths_with_obstacles(obstacle_grid):
    # Get the dimensions of the grid
    rows = len(obstacle_grid)
    cols = len(obstacle_grid[0])

    # --- Base Case: Check the Start ---
    # If the starting cell itself is an obstacle,
    # there are 0 paths.
    if obstacle_grid[0][0] == 1:
        return 0

    # --- 1. Tabular Instantiation ---
    # Create a DP table of the same size, initialized to 0.
    # dp[i][j] will store the number of unique paths to cell (i, j).
    dp = [[0 for _ in range(cols)] for _ in range(rows)]

    # --- 2. Initialization ---

    # There is 1 way to reach the starting cell (by starting there).
    dp[0][0] = 1

    # Initialize the first row.
    # A cell in the first row can only be reached from the left.
    for j in range(1, cols):
        if obstacle_grid[0][j] == 0:
            # If no obstacle, paths = paths from the left.
            dp[0][j] = dp[0][j - 1]
        # else: dp[0][j] remains 0 (it's an obstacle, 0 paths)

    # Initialize the first column.
    # A cell in the first column can only be reached from above.
    for i in range(1, rows):
        if obstacle_grid[i][0] == 0:
            # If no obstacle, paths = paths from above.
            dp[i][0] = dp[i - 1][0]
        # else: dp[i][0] remains 0 (it's an obstacle, 0 paths)

    # --- 3. DP Computation ---
    # Iterate through the rest of the grid, starting from (1, 1).
    for i in range(1, rows):
        for j in range(1, cols):

            # If the current cell is an obstacle,
            # there are 0 paths to it.
            if obstacle_grid[i][j] == 1:
                dp[i][j] = 0
            else:
                # The number of paths to (i, j) is the sum of:
                # 1. Paths from the cell above (i-1, j)
                # 2. Paths from the cell to the left (i, j-1)
                dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

    # The final answer is the number of paths to the
    # bottom-right corner.
    return dp[rows - 1][cols - 1]


obstacle_grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
print(unique_paths_with_obstacles(obstacle_grid))

obstacle_grid = [[1, 0]]
print(unique_paths_with_obstacles(obstacle_grid))

obstacle_grid = [[0, 1, 0, 0]]
print(unique_paths_with_obstacles(obstacle_grid))
