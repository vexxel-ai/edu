# LeetCode Problems Index

This directory contains solutions to **9 unique LeetCode problems** across various topics including Dynamic Programming, Linked Lists, Arrays, Bit Manipulation, and Graph Theory.

---

## 📊 Problems by Category

### Dynamic Programming (6 problems)
- [198. House Robber](#198-house-robber) - Medium
- [322. Coin Change](#322-coin-change) - Medium
- [63. Unique Paths II](#63-unique-paths-ii) - Medium
- [72. Edit Distance](#72-edit-distance) - Hard
- [120. Triangle](#120-triangle) - Medium
- [209. Minimum Size Subarray Sum](#209-minimum-size-subarray-sum) - Medium

### Linked Lists (1 problem)
- [92. Reverse Linked List II](#92-reverse-linked-list-ii) - Medium

### Bit Manipulation (1 problem)
- [868. Binary Gap](#868-binary-gap) - Easy

### Graph Theory / BFS (1 problem)
- [433. Minimum Genetic Mutation](#433-minimum-genetic-mutation) - Medium

---

## 📝 Detailed Problem Information

### 198. House Robber
**Difficulty:** Medium
**Topics:** Dynamic Programming, Array
**LeetCode:** https://leetcode.com/problems/house-robber/

**Description:**
You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. The only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and will automatically contact the police if two adjacent houses were broken into on the same night.

**Key Constraint:** Cannot rob two adjacent houses

**Solution Files:**
- `prob_198_0.py` - Solution approach 1
- `prob_198_1.py` - Solution approach 2

**Example:**
- Input: `[1,2,3,1]`
- Output: `4` (Rob house 1 and house 3: 1 + 3 = 4)

**Complexity:**
- Time: O(n)
- Space: O(1) with optimized approach

**Key Concept:** Use DP where `dp[i] = max(nums[i] + dp[i-2], dp[i-1])`

---

### 322. Coin Change
**Difficulty:** Medium
**Topics:** Dynamic Programming, Breadth-First Search
**LeetCode:** https://leetcode.com/problems/coin-change/

**Description:**
You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money. Return the fewest number of coins needed to make up that amount. If that amount cannot be made up by any combination, return -1.

**Key Constraint:** You have an infinite number of each kind of coin

**Solution Files:**
- `prob_322_0.py` - Solution approach 1
- `prob_322_1.py` - Solution approach 2

**Example:**
- Input: `coins = [1,2,5], amount = 11`
- Output: `3` (11 = 5 + 5 + 1)

**Complexity:**
- Time: O(S*n) where S is amount, n is number of coins
- Space: O(S)

**Key Concept:** Classic DP problem, build up solutions from smaller amounts

---

### 63. Unique Paths II
**Difficulty:** Medium
**Topics:** Array, Dynamic Programming, Matrix
**LeetCode:** https://leetcode.com/problems/unique-paths-ii/

**Description:**
A robot is located at the top-left corner of an m x n grid and tries to reach the bottom-right corner. The robot can only move either down or right at any point in time. An obstacle and space are marked as 1 or 0 respectively in the grid. A path that the robot takes cannot include any square that is an obstacle.

**Key Constraint:** Cannot pass through obstacles (marked as 1)

**Solution Files:**
- `prob_63_0.py`

**Example:**
- Input: `obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]`
- Output: `2` (There are two ways to reach the bottom-right corner)

**Complexity:**
- Time: O(m * n)
- Space: O(m * n)

**Key Concept:** DP with obstacle checking

---

### 72. Edit Distance
**Difficulty:** Hard
**Topics:** String, Dynamic Programming
**LeetCode:** https://leetcode.com/problems/edit-distance/

**Description:**
Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`. You have the following three operations permitted: Insert a character, Delete a character, Replace a character.

**Also Known As:** Levenshtein Distance

**Solution Files:**
- `prob_72_0.py`

**Example:**
- Input: `word1 = "horse", word2 = "ros"`
- Output: `3` (horse -> rorse -> rose -> ros)

**Complexity:**
- Time: O(m * n)
- Space: O(m * n)

**Key Concept:** 2D DP table where `dp[i][j]` = minimum operations to convert `word1[0..i-1]` to `word2[0..j-1]`

---

### 868. Binary Gap
**Difficulty:** Easy
**Topics:** Bit Manipulation
**LeetCode:** https://leetcode.com/problems/binary-gap/

**Description:**
Given a positive integer `n`, find and return the longest distance between any two adjacent 1's in the binary representation of `n`. If there are no two adjacent 1's, return 0.

**Solution Files:**
- `prob_868_0.py`

**Example:**
- Input: `n = 22` (binary: "10110")
- Output: `2`

**Complexity:**
- Time: O(log n)
- Space: O(1)

**Key Concept:** Convert to binary, track positions of 1's, find max distance

---

### 92. Reverse Linked List II
**Difficulty:** Medium
**Topics:** Linked List
**LeetCode:** https://leetcode.com/problems/reverse-linked-list-ii/

**Description:**
Given the head of a singly linked list and two integers `left` and `right` where `left <= right`, reverse the nodes of the list from position `left` to position `right`, and return the reversed list.

**Solution Files:**
- `prob_92_0.py`

**Example:**
- Input: `head = [1,2,3,4,5], left = 2, right = 4`
- Output: `[1,4,3,2,5]`

**Complexity:**
- Time: O(n)
- Space: O(1)

**Key Concept:** Use dummy node, keep moving node to head of reversed section

---

### 209. Minimum Size Subarray Sum
**Difficulty:** Medium
**Topics:** Array, Binary Search, Sliding Window, Prefix Sum
**LeetCode:** https://leetcode.com/problems/minimum-size-subarray-sum/

**Description:**
Given an array of positive integers `nums` and a positive integer `target`, return the minimal length of a subarray whose sum is greater than or equal to `target`. If there is no such subarray, return 0.

**Solution Files:**
- `prob_209.py`

**Example:**
- Input: `target = 7, nums = [2,3,1,2,4,3]`
- Output: `2` (The subarray [4,3] has minimal length)

**Complexity:**
- Time: O(n) with sliding window
- Space: O(1)

**Key Concept:** Sliding window technique - expand right, contract left

**Follow-up:** Can also be solved in O(n log n) using binary search

---

### 433. Minimum Genetic Mutation
**Difficulty:** Medium
**Topics:** Hash Table, String, Breadth-First Search
**LeetCode:** https://leetcode.com/problems/minimum-genetic-mutation/

**Description:**
A gene string can be represented by an 8-character long string with choices from 'A', 'C', 'G', and 'T'. Return the minimum number of mutations needed to mutate from `startGene` to `endGene`. If there is no such mutation, return -1.

**Key Constraint:** All mutations must be in the gene bank

**Solution Files:**
- `prob_433.py`

**Example:**
- Input: `startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]`
- Output: `1`

**Complexity:**
- Time: O(n * m) where n is bank size, m is gene length (8)
- Space: O(n)

**Key Concept:** BFS to find shortest path through valid mutations

---

### 120. Triangle
**Difficulty:** Medium
**Topics:** Array, Dynamic Programming
**LeetCode:** https://leetcode.com/problems/triangle/

**Description:**
Given a triangle array, return the minimum path sum from top to bottom. For each step, you may move to an adjacent number of the row below.

**Solution Files:**
- `prob_120.py`

**Example:**
- Input: `[[2],[3,4],[6,5,7],[4,1,8,3]]`
- Output: `11` (2 + 3 + 5 + 1 = 11)

**Complexity:**
- Time: O(n²) where n is number of rows
- Space: O(n) with optimized approach

**Key Concept:** Bottom-up DP, work backwards from bottom row

**Follow-up:** Can you do this using only O(n) extra space?

---

## 📈 Statistics

**Total Problems:** 9
**Difficulty Distribution:**
- Easy: 1 (11%)
- Medium: 7 (78%)
- Hard: 1 (11%)

**Topic Distribution:**
- Dynamic Programming: 6
- Array: 4
- String: 2
- Linked List: 1
- Bit Manipulation: 1
- Graph Theory/BFS: 1

**Multiple Solutions:**
- Problem 198: 2 solutions
- Problem 322: 2 solutions

---

## 🎯 Recommended Study Order

### Beginner (Start Here)
1. **868. Binary Gap** (Easy) - Warm up with bit manipulation

### Dynamic Programming Track
2. **198. House Robber** - Classic DP intro
3. **120. Triangle** - Bottom-up DP
4. **322. Coin Change** - Classic coin change problem
5. **63. Unique Paths II** - 2D DP with obstacles
6. **72. Edit Distance** - Hard, but classic Levenshtein distance

### Array & Sliding Window
7. **209. Minimum Size Subarray Sum** - Sliding window technique

### Linked Lists
8. **92. Reverse Linked List II** - Pointer manipulation

### Graph Theory
9. **433. Minimum Genetic Mutation** - BFS shortest path

---

## 📚 Additional Resources

- **LeetCode Patterns:** https://seanprashad.com/leetcode-patterns/
- **NeetCode Roadmap:** https://neetcode.io/roadmap
- **AlgoMonster:** https://algo.monster/

---

## 🔗 Quick Links

| Problem | Difficulty | Topic | LeetCode Link |
|---------|-----------|-------|---------------|
| 63 | Medium | DP | [Link](https://leetcode.com/problems/unique-paths-ii/) |
| 72 | Hard | DP, String | [Link](https://leetcode.com/problems/edit-distance/) |
| 92 | Medium | Linked List | [Link](https://leetcode.com/problems/reverse-linked-list-ii/) |
| 120 | Medium | DP | [Link](https://leetcode.com/problems/triangle/) |
| 198 | Medium | DP | [Link](https://leetcode.com/problems/house-robber/) |
| 209 | Medium | Sliding Window | [Link](https://leetcode.com/problems/minimum-size-subarray-sum/) |
| 322 | Medium | DP | [Link](https://leetcode.com/problems/coin-change/) |
| 433 | Medium | BFS | [Link](https://leetcode.com/problems/minimum-genetic-mutation/) |
| 868 | Easy | Bit Manipulation | [Link](https://leetcode.com/problems/binary-gap/) |

---

*Last Updated: December 2024*
*Total Solutions: 12 files (9 unique problems, 3 with multiple approaches)*
