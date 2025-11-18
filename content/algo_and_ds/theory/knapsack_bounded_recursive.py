# Bounded Knapsack Problem

def bounded_knapsack_recursive(capacity, weights, profits):
    def aux(current_capacity, idx, memo):
        # --- 1. Base Case: No items left ---
        if idx >= len(weights):
            return 0

        # --- 2. Memoization Check ---
        # Define a unique key for the current state
        state_key = (idx, current_capacity)
        if state_key in memo:
            return memo[state_key]

        # --- 3. Recursive Step ---
        
        # Option 1: Exclude the current item
        # We move to the next item (idx + 1) keeping the same capacity.
        # This is always a valid move.
        max_profit = aux(current_capacity, idx + 1, memo)

        # Option 2: Include the current item (If it fits)
        current_weight = weights[idx]
        current_profit = profits[idx]
        
        if current_weight <= current_capacity:
            # Calculate profit if we include this item:
            # Item's profit + max profit from remaining items with reduced capacity.
            include_profit = current_profit + aux(current_capacity - current_weight, idx + 1, memo)
            
            # Does including it yield a better result than excluding it?
            max_profit = max(max_profit, include_profit)

        # --- 4. Store and Return ---
        memo[state_key] = max_profit
        return max_profit

    # Initialize the cache
    memo = {}
    # Start recursion from the first item (index 0)
    return aux(capacity, 0, memo)

# Inputs
capacity = 50
weights = [10, 20, 30]
profits = [60, 100, 120]
out_ = bounded_knapsack_recursive(capacity, weights, profits)
print(out_)
assert out_ == 220




