def coin_change_dp(coins, amount):
    # Create a DP table (array) of size 'amount + 1'.
    # dp[i] will store the minimum number of coins needed to make amount 'i'.
    dp = [float('inf') for _ in range(amount + 1)]

    # --- Initialization ---
    # The base case: It takes 0 coins to make an amount of 0.
    dp[0] = 0

    # --- Computation (Bottom-Up) ---
    # Iterate through all amounts from 1 up to the target amount.
    # 'i' represents the target amount we are currently trying to solve for.
    for i in range(1, amount + 1):
        # For each amount 'i', try every coin to see if we can use it
        for c in coins:
            # Calculate the remaining amount needed if we use the current coin 'c'.
            remainder_amount = i - c

            # We can only use this coin 'c' if:
            # 1. The remainder is not negative (remainder_amount >= 0).
            # 2. The subproblem for the remainder (dp[remainder_amount]) has a reachable solution
            # (i.e., it's not still 'inf').
            if remainder_amount >= 0 and dp[remainder_amount] != float('inf'):
                # If we use coin 'c', the total coins for this path is:
                # 1 (for coin 'c') + the best solution for the remainder.
                # This is the core DP recurrence relation.
                num_of_coins = 1 + dp[remainder_amount]

                # We want the *minimum* number of coins.
                # Is the path using coin 'c' (num_of_coins) better than the
                # best path we've found so far for this amount (dp[i])?
                dp[i] = min(dp[i], num_of_coins)

    # After all loops are done, dp[amount] holds the final answer.

    # If dp[amount] is still 'inf', it means we were never able
    # to find a valid coin combination for the target amount.
    # Otherwise, we return the calculated minimum.
    return dp[amount] if dp[amount] != float('inf') else -1


"""
--- Example 1:
Input: coins = [1,2,5], amount = 11
Output: 3
Explanation: 11 = 5 + 5 + 1
"""

coins = [1, 2, 5]
amount = 11
assert coin_change_dp(coins, amount) == 3
print(coin_change_dp(coins, amount))

"""
Example 2:
Input: coins = [2], amount = 3
Output: -1
Example 3:
"""
coins = [2]
amount = 3
assert coin_change_dp(coins, amount) == -1
print(coin_change_dp(coins, amount))

"""
Input: coins = [1], amount = 0
Output: 0
"""
coins = [11]
amount = 0
assert coin_change_dp(coins, amount) == 0
print(coin_change_dp(coins, amount))
