# Reference: https://www.youtube.com/watch?v=73r3KWiEvyk

def rob_recursive(nums):
    # A dictionary to store the results of subproblems
    memo = {}

    def solve(i):
        if i in memo:
            return memo[i]

        # Base case: No houses, no money
        if i < 0:
            return 0

        # Base case: One house, rob it
        if i == 0:
            return nums[0]

        # 1. Choice: Rob house i (nums[i]) + max money from houses 0...i-2
        rob_this_house = nums[i] + solve(i - 2)

        # 2. Choice: skip house i = max money from houses 0...i-1
        skip_this_house = solve(i - 1)

        # Store the best choise in our memo
        memo[i] = max(rob_this_house, skip_this_house)
        return memo[i]

    # Start the recursion fom the last house
    return solve(len(nums) - 1)


# Input 1
nums = [1, 2, 3, 1]
# Expected output = 4
print("Houses: ", nums)
print("Total amount: ", rob_recursive(nums))
assert rob_recursive(nums) == 4

# Input 2
nums = [2, 7, 9, 3, 1]
# Expected output = 12
print("Houses: ", nums)
print("Total amount: ", rob_recursive(nums))
assert rob_recursive(nums) == 12

