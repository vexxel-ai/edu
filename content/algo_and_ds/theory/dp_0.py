# Grid World Problem

def count_paths_brute_force(m, n):
    """
    Calculates the number of paths from (0, 0) to (m-1, n-1)
    using a brute-force recursive approach.
    """

    def explore(row, col):
        # Base Case 1: Out of bounds
        # If we move off the grid, this path is invalid.
        if row >= m or col >= n:
            return 0

        # Base Case 2: Reached the destination
        # If we are at the bottom-right square, we found 1 valid path.
        if row == m - 1 and col == n - 1:
            return 1

        # Recursive Step:
        # The total paths from this square are the sum of:
        # 1. Paths from moving DOWN (explore(row + 1, col))
        # 2. Paths from moving RIGHT (explore(row, col + 1))
        return explore(row + 1, col) + explore(row, col + 1)

    # Start the exploration from the top-left corner (0, 0)
    return explore(0, 0)


# --- 4x4 grid example ---
m_rows = 4
n_cols = 4

total_paths = count_paths_brute_force(m_rows, n_cols)

print(f"Grid Size: {m_rows}x{n_cols}")
print(f"Total Unique Paths (Brute Force): {total_paths}")