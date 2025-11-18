def min_distance(word1, word2):
    def aux(len_word1, len_word2, memo):
        """
        This is our recursive helper function. It answers the question: "What is the minimum 
        cost to convert the first 'len_word1' characters of word1 into the first 'len_word2' characters of word2?"
        e.g., aux(3, 2) for "horse", "ros" asks: "What's the cost to convert 'hor' into 'ro'?"
        """

        # --- 1. Memoization Check ---
        if (len_word1, len_word2) in memo:
            return memo[(len_word1, len_word2)]

        # --- 2. Base Cases ---
        # If word2 is empty (""), we must convert word1 to "".
        if len_word2 == 0:
            return len_word1 # The only way is to delete all 'len_word1' characters.
        # If word1 is empty (""), we must convert "" to word2.
        if len_word1 == 0:
            return len_word2 # The only way is to insert all 'len_word2' characters.

        # --- 3. Recursive Step ---
        # Look at the last character of each substring. (e.g., for "hor" and "ro", we look at 'r' and 'o'.)
        if word1[len_word1 - 1] == word2[len_word2 - 1]:
            # The last characters match! (e.g., "hors" and "ros")
            # No operation is needed for this character ('s').
            # The cost is 0 + the cost of the subproblem. (i.e., "hor" -> "ro").
            result = aux(len_word1 - 1, len_word2 - 1, memo)
        else:
            # The last characters do NOT match (e.g., "horse" and "ros")
            # We must perform an operation. We try all 3 and pick the one with the minimum cost.

            # -- Choice 1: Insert
            # We "insert" 's' onto "horse" to match "ros".
            # Cost = 1 (for the insert) + cost("horse" -> "ro")
            num_of_ops_i = 1 + aux(len_word1, len_word2 - 1, memo)

            # -- Choice 2: Delete
            # We "delete" 'e' from "horse".
            # Cost = 1 (for the delete) + cost("hors" -> "ros")
            num_of_ops_d = 1 + aux(len_word1 - 1, len_word2, memo)

            # -- Choice 3: Replace
            # We "replace" 'e' in "horse" with 's'.
            # Cost = 1 (for the replace) + cost("hors" -> "ro")
            num_of_ops_r = 1 + aux(len_word1 - 1, len_word2 - 1, memo)

            result = min(num_of_ops_i, num_of_ops_d, num_of_ops_r) # We pick the cheapest of the 3 choices.

        # --- 4. Save and Return ---
        memo[(len_word1, len_word2)] = result
        return result

    # Create the cache (memo) to store results
    memo = {}
    # Start the whole process by asking for the solution for the full strings.
    return aux(len(word1), len(word2), memo)



word1 = "horse"
word2 = "ros"
print(min_distance(word1, word2))
