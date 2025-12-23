def minimum_total(triangle):
    # Initialize memo
    memo = {}

    def dfs(row, col):
        # 1. Check memo
        if (row, col) in memo:
            return memo[(row, col)]
        
        # 2. Base case
        # -- If we go past the bottom row, there is no more value to be added
        if row == len(triangle):
            return 0
        
        # 3. Recursive Step
        lower_left = dfs(row + 1, col)
        lower_right = dfs(row + 1, col + 1)

        # 4. Calculation
        current_val = triangle[row][col]
        result = current_val + min(lower_left, lower_right)

        # 5. Store in memo
        memo[(row, col)] = result
        return result
    
    return dfs(0, 0)

triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
output = minimum_total(triangle)
print(output)
