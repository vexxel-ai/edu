# Kadane's Algorithm: A Dynamic Programming Masterpiece

Kadane's Algorithm stands as one of the most elegant examples of dynamic programming in computer science. Despite its apparent simplicity, this algorithm demonstrates profound insights into optimization and showcases how clever thinking can reduce seemingly complex problems to remarkably efficient solutions. The maximum subarray problem it solves appears frequently in real-world applications, from analyzing stock market data to signal processing and bioinformatics.

## The Maximum Subarray Problem

Given an array of integers (which may include negative numbers, positive numbers, or both), find the contiguous subarray that has the largest sum. The subarray must be non-empty and maintain the original order of elements.

**Classic Example:**
```
Input: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Output: 6
Explanation: The subarray [4, -1, 2, 1] has the largest sum of 6
```

At first glance, you might consider checking every possible subarray—there are O(n²) such subarrays in an array of length n. For each subarray, computing its sum takes O(n) time in the worst case, leading to a brute-force O(n³) solution. We can optimize this to O(n²) using prefix sums, but Kadane's Algorithm achieves the optimal O(n) time complexity with O(1) space.

## The Elegant Solution

Kadane's Algorithm is based on a beautiful insight: at each position in the array, we face a simple decision—should we extend the current subarray by including this element, or should we start a completely new subarray from this element?

Here's the complete implementation:

```python
def kadane(arr):
    '''
    Find the maximum sum of any contiguous subarray.

    Args:
        arr: List of integers (can include negative numbers)

    Returns:
        Integer representing the maximum subarray sum
    '''
    if not arr:
        raise ValueError("Array must be non-empty")

    # max_ending_here: maximum sum of subarray ending at current position
    max_ending_here = arr[0]

    # max_so_far: maximum sum found so far (global maximum)
    max_so_far = arr[0]

    for i in range(1, len(arr)):
        # Key decision: extend current subarray or start new one?
        # If max_ending_here is negative, starting fresh is better
        max_ending_here = max(arr[i], max_ending_here + arr[i])

        # Update global maximum if we found a better sum
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far

# Example usage
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
result = kadane(arr)
print(f"Maximum subarray sum: {result}")  # Output: 6
```

## Understanding the Algorithm Through Dynamic Programming

Kadane's Algorithm is fundamentally a dynamic programming solution, though its elegance makes this less obvious than traditional DP implementations.

**Define the Subproblem:**
Let `dp[i]` represent the maximum sum of any subarray that **ends at index i**.

**Recurrence Relation:**
```
dp[i] = max(arr[i], dp[i-1] + arr[i])
```

This says: the best subarray ending at position i is either:
1. Just the element arr[i] itself (starting a new subarray)
2. The best subarray ending at i-1, extended to include arr[i]

**Base Case:**
```
dp[0] = arr[0]
```

The answer to our problem is:
```
max(dp[0], dp[1], dp[2], ..., dp[n-1])
```

Kadane's Algorithm implements this DP solution with O(1) space by observing that we only need the previous `dp` value, not the entire array of `dp` values.

## Step-by-Step Execution

Let's trace through the algorithm with our example array:

```
Array: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Index:  0   1   2  3   4  5  6   7  8

i=0: max_ending_here = -2, max_so_far = -2
     Starting with first element

i=1: max_ending_here = max(1, -2+1) = max(1, -1) = 1
     max_so_far = max(-2, 1) = 1
     Better to start fresh at 1

i=2: max_ending_here = max(-3, 1+(-3)) = max(-3, -2) = -2
     max_so_far = max(1, -2) = 1
     Extend, but sum becomes negative

i=3: max_ending_here = max(4, -2+4) = max(4, 2) = 4
     max_so_far = max(1, 4) = 4
     Better to start fresh at 4

i=4: max_ending_here = max(-1, 4+(-1)) = max(-1, 3) = 3
     max_so_far = max(4, 3) = 4
     Extend: [4, -1]

i=5: max_ending_here = max(2, 3+2) = max(2, 5) = 5
     max_so_far = max(4, 5) = 5
     Extend: [4, -1, 2]

i=6: max_ending_here = max(1, 5+1) = max(1, 6) = 6
     max_so_far = max(5, 6) = 6
     Extend: [4, -1, 2, 1]

i=7: max_ending_here = max(-5, 6+(-5)) = max(-5, 1) = 1
     max_so_far = max(6, 1) = 6
     Extend but sum drops: [4, -1, 2, 1, -5]

i=8: max_ending_here = max(4, 1+4) = max(4, 5) = 5
     max_so_far = max(6, 5) = 6
     Extend: [4, -1, 2, 1, -5, 4]

Final answer: 6 (from subarray [4, -1, 2, 1])
```

## Finding the Actual Subarray

The basic algorithm returns only the maximum sum. If we also need the subarray indices:

```python
def kadane_with_indices(arr):
    '''
    Find maximum subarray sum and return sum, start index, and end index.

    Returns:
        Tuple of (max_sum, start_index, end_index)
    '''
    max_ending_here = arr[0]
    max_so_far = arr[0]

    start = 0  # Start of maximum subarray
    end = 0    # End of maximum subarray
    temp_start = 0  # Temporary start position

    for i in range(1, len(arr)):
        # If starting fresh, update temporary start
        if arr[i] > max_ending_here + arr[i]:
            max_ending_here = arr[i]
            temp_start = i
        else:
            max_ending_here = max_ending_here + arr[i]

        # Update global maximum
        if max_ending_here > max_so_far:
            max_so_far = max_ending_here
            start = temp_start
            end = i

    return max_so_far, start, end

# Example
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
max_sum, start, end = kadane_with_indices(arr)
print(f"Maximum sum: {max_sum}")
print(f"Subarray: arr[{start}:{end+1}] = {arr[start:end+1]}")
# Output: Maximum sum: 6
#         Subarray: arr[3:7] = [4, -1, 2, 1]
```

## Complexity Analysis

**Time Complexity: O(n)**
- Single pass through the array
- Constant time operations per element
- Optimal for this problem (must examine every element)

**Space Complexity: O(1)**
- Only a constant number of variables
- No additional data structures
- Space-optimized dynamic programming

This makes Kadane's Algorithm extremely efficient, even for arrays with millions of elements.

## Important Edge Cases

**All Negative Numbers:**
```python
arr = [-5, -2, -8, -1, -4]
result = kadane(arr)  # Returns -1 (the largest single element)
```

**Single Element:**
```python
arr = [5]
result = kadane(arr)  # Returns 5
```

**All Positive Numbers:**
```python
arr = [1, 2, 3, 4, 5]
result = kadane(arr)  # Returns 15 (entire array)
```

**Mix with Zero:**
```python
arr = [-1, 0, -2, 3, 4, -1]
result = kadane(arr)  # Returns 7 ([3, 4])
```

## Variations and Related Problems

### Maximum Product Subarray

Instead of sum, find the maximum product. This requires tracking both maximum and minimum (since negative × negative = positive):

```python
def max_product_subarray(arr):
    if not arr:
        return 0

    max_so_far = arr[0]
    max_ending_here = arr[0]
    min_ending_here = arr[0]

    for i in range(1, len(arr)):
        temp_max = max(arr[i], max_ending_here * arr[i], min_ending_here * arr[i])
        min_ending_here = min(arr[i], max_ending_here * arr[i], min_ending_here * arr[i])
        max_ending_here = temp_max
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far
```

### Maximum Circular Subarray

Handle arrays that wrap around (circular):

```python
def max_circular_subarray(arr):
    # Case 1: Maximum subarray is in the middle (use Kadane's)
    max_kadane = kadane(arr)

    # Case 2: Maximum subarray wraps around
    # This equals: total_sum - minimum_subarray
    max_wrap = sum(arr) - kadane([-x for x in arr])

    # Handle all negative case
    if max_wrap == 0:
        return max_kadane

    return max(max_kadane, max_wrap)
```

### Maximum Sum with At Least K Elements

Find maximum sum subarray with at least k elements:

```python
def max_sum_at_least_k(arr, k):
    max_sum = sum(arr[:k])
    current_sum = max_sum
    min_prefix = 0
    prefix_sum = 0

    for i in range(k, len(arr)):
        current_sum += arr[i]
        prefix_sum += arr[i - k]
        min_prefix = min(min_prefix, prefix_sum)
        max_sum = max(max_sum, current_sum - min_prefix)

    return max_sum
```

## Real-World Applications

**Stock Trading**: Given daily price changes, find the best period to hold a stock for maximum profit.

**Signal Processing**: Identify segments in a signal with maximum energy or amplitude.

**Bioinformatics**: Find regions of DNA sequences with specific properties (GC content, hydrophobicity).

**Image Processing**: Detect regions of images with maximum cumulative brightness or contrast.

**Resource Allocation**: Determine optimal time windows for resource usage to maximize benefit.

## Practice Problems

1. **LeetCode 53 - Maximum Subarray** (Easy): Direct application
2. **LeetCode 152 - Maximum Product Subarray** (Medium): Product variation
3. **LeetCode 918 - Maximum Sum Circular Subarray** (Medium): Circular variation
4. **LeetCode 1186 - Maximum Subarray Sum with One Deletion** (Medium): With modification
5. **LeetCode 1191 - K-Concatenation Maximum Sum** (Medium): Array repetition

## Why This Algorithm Matters

Kadane's Algorithm beautifully demonstrates several key computer science principles:

1. **Dynamic Programming**: Optimal substructure and overlapping subproblems
2. **Greedy Choice**: Making locally optimal decisions (extend or start new)
3. **Space Optimization**: Reducing O(n) space to O(1)
4. **Problem Transformation**: Viewing the problem through the lens of "ending at position i"

It's a testament to the power of algorithmic thinking—transforming what seems like a quadratic problem into a linear solution through careful observation and clever design.

The handwritten notes and visualizations below provide step-by-step walkthroughs that will deepen your understanding of this fundamental algorithm!
