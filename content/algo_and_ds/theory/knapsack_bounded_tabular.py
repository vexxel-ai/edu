# Bounded Knapsack

def bounded_knapsack_tabular(capacity, weights, profits):
    num_items = len(weights)

    # dp[i][w] stores the maximum value that can be achieved 
    # with the first 'i' items and a maximum weight of 'w'.
    dp_table = [[0 for _ in range(capacity + 1)] for _ in range(num_items + 1)]

    # Iterate through each item (row)
    for i in range(1, num_items + 1):

        current_weight = weights[i - 1]
        current_profit = profits[i - 1]
        # Iterate through each possible capacity (column)

        for cap_ in range(1, capacity + 1):
            # Case 1: The current item CAN be included
            if cap_ >= current_weight:
                # -- Value if item is INCLUDED:
                # current item's value + max value from previous items (i-1)
                # using the remaining capacity (w - current_weight)
                value_if_included = current_profit + dp_table[i - 1][cap_ - current_weight]

                # -- Value if item is EXCLUDED:
                # Max value from previous items (i-1) using the same capacity (w)
                value_if_excluded = dp_table[i - 1][cap_]

                # -- The maximum profit at this cell is the max of the two options
                dp_table[i][cap_] = max(value_if_included, value_if_excluded)
                
            # Case 2: The current item CANNOT be included
            else:
                # Inherit the max value from the previous item (i-1) with the same capacity (w)
                dp_table[i][cap_] = dp_table[i - 1][cap_]

    # The final answer is the bottom-right cell
    return dp_table[num_items][capacity]


# Inputs
capacity = 5
weights = [1, 2, 3]
profits = [6, 10, 12]
out_ = bounded_knapsack_tabular(capacity, weights, profits)
print(out_)
assert out_ == 22
