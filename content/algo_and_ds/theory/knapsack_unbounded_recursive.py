def unbounded_knapsack_recursive(capacity, weights, profits):
    def get_max_profit(remaining_capacity, idx, memo):
        # --- 1. Base Case: No items left to consider ---
        if idx >= len(weights):
            return 0

        # --- 2. Memoization Check ---
        # The state is defined by (current item being considered, remaining capacity)
        state_key = (idx, remaining_capacity)
        if state_key in memo:
            return memo[state_key]

        # --- 3. Recursive Step: Two main choices for the current item (idx) ---
        current_weight = weights[idx]
        current_profit = profits[idx]

        # Choice 1: Exclude the current item (Go to next item, same capacity)
        # This is always a valid move.
        profit_exclude = get_max_profit(remaining_capacity, idx + 1, memo)

        # Choice 2: Include the current item (Only if it fits)
        profit_include = 0

        if remaining_capacity >= current_weight:
            # If we include the item, the profit is:
            # Current profit + (Max profit from the remaining capacity and the CURRENT item list).
            # We call 'idx' again to allow for multiple uses of this item.
            profit_include = current_profit + get_max_profit(remaining_capacity - current_weight, idx, memo)

        # The result is the maximum of excluding the item or including it.
        max_profit = max(profit_exclude, profit_include)

        # --- 4. Store and Return ---
        memo[state_key] = max_profit
        return max_profit

    # --- Start the Recursion ---
    memo = {}
    return get_max_profit(capacity, 0, memo)

# Inputs
capacity = 7
weights = [1, 3, 4]
profits = [15, 20, 30]
out_ = unbounded_knapsack_recursive(capacity, weights, profits)
print(out_)
assert out_ == 105
