def count_paths_tabular(m_rows, n_cols):
    """
    Calculates the number of paths from (0, 0) to (m-1, n-1)
    using a bottom-up dynamic programming (tabulation) approach.
    """

    # 1. Create the DP table (grid)
    # This table will store the number of paths to reach *each* cell (i, j).
    # We initialize it with a placeholder (like 0).
    dp = [[0 for _ in range(n_cols)] for _ in range(m_rows)]

    # 2. Initialization (Set Base Cases)

    # There is exactly 1 way to reach the starting cell (0, 0).
    dp[0][0] = 1

    # -- Fill the first row --
    # You can only reach a cell in the first row by moving right from the
    # cell to its left. So, there's only 1 path to each.
    for j in range(1, n_cols):
        dp[0][j] = 1  # Inherits the 1 path from dp[0][j-1]

    # -- Fill the first column --
    # Similarly, you can only reach a cell in the first column by moving down
    # from the cell above it. So, there's only 1 path to each.
    for i in range(1, m_rows):
        dp[i][0] = 1  # Inherits the 1 path from dp[i-1][0]

    # 3. Compute the rest of the grid
    # Iterate through every other cell starting from (1, 1).
    for i in range(1, m_rows):
        for j in range(1, n_cols):
            # The number of paths to this cell is the sum of:
            #   1. The number of paths to the cell ABOVE it (dp[i-1][j])
            #   2. The number of paths to the cell to its LEFT (dp[i][j-1])
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

    # 4. Return the final answer
    # The value in the bottom-right cell holds the total
    # number of paths to reach the destination.
    print(dp)
    return dp[m_rows - 1][n_cols - 1]


# --- 4x4 grid example ---
m_rows = 4
n_cols = 4

total_paths = count_paths_tabular(m_rows, n_cols)

print(f"Grid Size: {m_rows}x{n_cols}")
print(f"Total Unique Paths (Tabular DP): {total_paths}")