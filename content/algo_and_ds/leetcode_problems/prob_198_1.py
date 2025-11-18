def rob(nums):
    prev_one = 0 # The max profit from the previous house (i.e., dp[i-1])
    prev_two = 0 # The max profit from two houses ago (i.e., dp[i-2])

    # Loop through each house
    for money in nums:
        # At each house, we have a choice:
        # 1. Rob this house: money + prev_two (can't rob prev_one)
        # 2. Skip this house: prev_one (we keep the max from the last step)
        curr_max = max(money + prev_two, prev_one)

        # Now, update the variables for the *next* loop iteration:
        # The "one_house_ago" profit becomes the "two_houses_ago" profit
        # The "current_max" profit becomes the "one_house_ago" profit
        prev_two = prev_one
        prev_one = curr_max

    return prev_one


# Input 1
nums = [1, 2, 3, 1]
# Expected output = 4
print("Houses: ", nums)
print("Total amount: ", rob(nums))
assert rob(nums) == 4

# Input 2
nums = [2, 7, 9, 3, 1]
# Expected output = 12
print("Houses: ", nums)
print("Total amount: ", rob(nums))
assert rob(nums) == 12
