def coin_change(coins, amount):
    def aux(coins, amount, memo):
        # Base Cases
        # -- Base case 1: no solution
        if amount < 0:
            return float('inf')
        # -- Base case 2: bottom of the tree
        if amount == 0:
            return 0

        # memoization to improve speed
        if amount in memo:
            return memo[amount]

        # We need to evaluate all coins
        num_of_coins_for_amount = float('inf')
        for c in coins:
            curr_amount = amount - c
            num_of_coins_for_curr_amount = 1 + aux(coins, curr_amount, memo)
            num_of_coins_for_amount = min(num_of_coins_for_amount, num_of_coins_for_curr_amount)

        memo[amount] = num_of_coins_for_amount
        return memo[amount]

    # Base case
    if amount == 0:
        return 0
    memo = {}
    aux(coins, amount, memo)
    num_of_coins = memo[amount]
    return num_of_coins if num_of_coins != float('inf') else -1


"""
--- Example 1:
Input: coins = [1,2,5], amount = 11
Output: 3
Explanation: 11 = 5 + 5 + 1
"""

coins = [1, 2, 5]
amount = 11
print(coin_change(coins, amount))

"""
Example 2:
Input: coins = [2], amount = 3
Output: -1
Example 3:
"""
coins = [2]
amount = 3
print(coin_change(coins, amount))

"""
Input: coins = [1], amount = 0
Output: 0
"""
coins = [11]
amount = 0
print(coin_change(coins, amount))
