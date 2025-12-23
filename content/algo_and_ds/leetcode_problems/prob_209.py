# Minimum Size Subarray Sum

def min_subarray_len(target: int, nums: list[int]) -> int:
    # Initialize the minimum length found so far
    min_length = float('inf')

    # Track the sum of the elements within the current window
    current_sum = 0

    # (Left pointer) marks the beginning of the current window
    window_start = 0

    # The 'window_end' (Right pointer) expands the window 
    # one element at at time
    for window_end, num in enumerate(nums):
        # Expand the window and update the sum
        current_sum += num

        # Contraction phase: shrink the window while
        # the target condition is satified
        while current_sum >= target:
            # Calculate the length of the current valid sublist
            current_length = window_end - window_start + 1

            # Update the overall minimum length
            min_length = min(min_length, current_length)

            # Shrink the window from the left (contract)
            current_sum -= nums[window_start]

            # Move the left pointer one step to the right
            window_start += 1

    return min_length if min_length != float('inf') else 0

nums = [2, 3, 1, 2, 4, 3]
target = 7
print(min_subarray_len(target, nums))

