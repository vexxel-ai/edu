# Longest Increasing Subsequence (LIS)

## Problem Statement

Given an integer array `nums`, return the length of the longest strictly increasing subsequence.

A **subsequence** is a sequence that can be derived from an array by deleting some or no elements without changing the order of the remaining elements.

## Dynamic Programming Approach

This is a classic DP problem that demonstrates optimal substructure and overlapping subproblems.

### State Definition

Let `dp[i]` = length of the longest increasing subsequence ending at index `i`.

### Recurrence Relation

For each position `i`, we look at all previous positions `j` where `j < i`:

```
dp[i] = max(dp[j] + 1) for all j < i where nums[j] < nums[i]
```

If no such `j` exists, then `dp[i] = 1` (the element itself forms a subsequence of length 1).

### Algorithm Steps

1. Initialize `dp[i] = 1` for all `i` (each element is a subsequence of length 1)
2. For each `i` from 1 to n-1:
   - For each `j` from 0 to i-1:
     - If `nums[j] < nums[i]`, update `dp[i] = max(dp[i], dp[j] + 1)`
3. Return `max(dp)`

### Complexity Analysis

- **Time Complexity**: O(n²) - nested loops
- **Space Complexity**: O(n) - dp array

### Example Walkthrough

```
nums = [10, 9, 2, 5, 3, 7, 101, 18]

dp   = [1,  1, 1, 1, 1, 1,  1,   1]  (initial)

After processing:
dp   = [1,  1, 1, 2, 2, 3,  4,   4]

LIS length = 4
One possible LIS: [2, 3, 7, 101] or [2, 3, 7, 18]
```

## Optimized Approach: Binary Search + Patience Sorting

There's an O(n log n) solution using binary search, which maintains an array of the smallest ending elements for all increasing subsequences of each length.

This approach is based on the "patience sorting" algorithm and is more advanced.
