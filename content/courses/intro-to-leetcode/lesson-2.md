# Array Fundamentals: Master the Most Common Data Structure

## Introduction

Arrays are the most frequently tested data structure in coding interviews. Master these patterns and you'll solve 40%+ of LeetCode problems.

## What Makes Arrays Special?

**Key characteristics:**
- **Contiguous memory**: Elements stored side-by-side
- **O(1) access time**: Direct index lookup
- **Fixed or dynamic size**: Arrays (fixed) vs Lists (dynamic)
- **Cache-friendly**: Sequential access is fast

## Core Array Patterns

### 1. Two Pointers

Used when you need to compare or combine elements from both ends.

```python
def reverse_array(arr):
    """Reverse array in-place using two pointers"""
    left, right = 0, len(arr) - 1

    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1

    return arr

# Example
nums = [1, 2, 3, 4, 5]
reverse_array(nums)  # [5, 4, 3, 2, 1]
```

**When to use:**
- Finding pairs that sum to a target
- Reversing arrays/strings
- Removing duplicates from sorted arrays

### 2. Sliding Window

Process subarrays of fixed or variable size efficiently.

```python
def max_subarray_sum(arr, k):
    """
    Find maximum sum of k consecutive elements.

    Example: arr = [2, 1, 5, 1, 3, 2], k = 3
    Output: 9 (subarray [5, 1, 3])
    """
    if len(arr) < k:
        return 0

    # Calculate initial window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide the window
    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)

    return max_sum
```

**When to use:**
- Finding subarrays with specific properties
- String problems with substrings
- Optimization problems on contiguous elements

### 3. Prefix Sum

Precompute cumulative sums for O(1) range queries.

```python
class PrefixSum:
    def __init__(self, nums):
        """Build prefix sum array"""
        self.prefix = [0]
        for num in nums:
            self.prefix.append(self.prefix[-1] + num)

    def range_sum(self, left, right):
        """Get sum of elements from index left to right"""
        return self.prefix[right + 1] - self.prefix[left]

# Example
nums = [1, 2, 3, 4, 5]
ps = PrefixSum(nums)
print(ps.range_sum(1, 3))  # Output: 9 (2+3+4)
```

**When to use:**
- Multiple range sum queries
- Subarray sum problems
- 2D matrix sum queries

## Practice Problem: Container With Most Water

**Problem:** Given heights of vertical lines, find two lines that form a container holding the most water.

```python
def max_area(height):
    """
    Two-pointer approach to find maximum area.

    Time: O(n), Space: O(1)
    """
    left, right = 0, len(height) - 1
    max_water = 0

    while left < right:
        # Calculate current area
        width = right - left
        current_height = min(height[left], height[right])
        max_water = max(max_water, width * current_height)

        # Move pointer with smaller height
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water

# Example
heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]
print(max_area(heights))  # Output: 49
```

**Why this works:**
- Start with maximum width (full array)
- Moving inward only makes sense if we might find taller lines
- Greedy approach: always move the shorter pointer

## Time Complexity Cheat Sheet

| Operation | Array | Dynamic Array |
|-----------|-------|---------------|
| Access | O(1) | O(1) |
| Search | O(n) | O(n) |
| Insert (end) | N/A | O(1) amortized |
| Insert (middle) | N/A | O(n) |
| Delete | N/A | O(n) |

## Key Takeaways

1. **Two pointers** → pairs, reversing, sorted arrays
2. **Sliding window** → subarrays, optimization
3. **Prefix sum** → range queries, cumulative data
4. Always consider **time/space tradeoffs**

## Practice Exercises

Try these LeetCode problems:
- Easy: Best Time to Buy and Sell Stock (#121)
- Medium: Product of Array Except Self (#238)
- Hard: Trapping Rain Water (#42)

---

**Next Lesson:** We'll explore HashMap patterns and how to optimize lookups to O(1).
