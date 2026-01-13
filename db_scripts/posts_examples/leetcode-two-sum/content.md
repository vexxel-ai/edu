# Two Sum Problem

## Problem Statement

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

## Approach

The brute force approach would be O(n²), checking every pair of numbers. However, we can optimize this to O(n) using a hash map.

### Key Insight

For each number `nums[i]`, we need to find if `target - nums[i]` exists in the array. Instead of searching the entire array each time, we can store seen numbers in a hash map for O(1) lookup.

### Algorithm

1. Create an empty hash map `seen = {}`
2. For each element at index `i`:
   - Calculate `complement = target - nums[i]`
   - If `complement` exists in `seen`, return `[seen[complement], i]`
   - Otherwise, store `nums[i]` with its index: `seen[nums[i]] = i`

### Complexity Analysis

- **Time Complexity**: O(n) - single pass through the array
- **Space Complexity**: O(n) - hash map stores at most n elements

## Example

```
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
Explanation: nums[0] + nums[1] = 2 + 7 = 9
```

## Related Patterns

- Hash map for O(1) lookup
- Two-pointer technique (for sorted arrays)
- Complement search pattern
