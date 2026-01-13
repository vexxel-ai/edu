# Merge Intervals

## Problem Statement

Given an array of intervals where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals and return an array of the non-overlapping intervals.

## Sorting Approach

The key insight is to **sort the intervals by start time first**. Once sorted, overlapping intervals will be adjacent to each other.

### Algorithm

1. Sort intervals by start time
2. Initialize result list with first interval
3. For each subsequent interval:
   - If it overlaps with the last interval in result, merge them
   - Otherwise, add it as a new interval

### Overlap Condition

Two intervals `[a, b]` and `[c, d]` overlap if:
- `c <= b` (assuming `a <= c` after sorting)

When merging, the new interval is:
- `[a, max(b, d)]`

### Complexity Analysis

- **Time Complexity**: O(n log n) - dominated by sorting
- **Space Complexity**: O(n) - for the result array

### Example Walkthrough

```
Input: [[1,3], [2,6], [8,10], [15,18]]

After sorting by start: [[1,3], [2,6], [8,10], [15,18]]

Step 1: result = [[1,3]]
Step 2: [2,6] overlaps with [1,3] (2 <= 3)
        Merge: [1, max(3,6)] = [1,6]
        result = [[1,6]]
Step 3: [8,10] doesn't overlap with [1,6] (8 > 6)
        result = [[1,6], [8,10]]
Step 4: [15,18] doesn't overlap with [8,10] (15 > 10)
        result = [[1,6], [8,10], [15,18]]
```

## Edge Cases

1. **Empty input**: Return empty array
2. **Single interval**: Return as is
3. **All intervals overlap**: Return single merged interval
4. **No overlaps**: Return sorted intervals unchanged
5. **Intervals with same start**: Sorting handles this correctly
