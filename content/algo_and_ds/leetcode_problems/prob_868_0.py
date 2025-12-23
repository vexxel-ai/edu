def binary_gap(n: int) -> int:
    # 1. Convert to Binary String
    binary_n = bin(n)[2:] # bin(n) returns "0b...", let's slice it

    # 2. Initialize variables
    max_distance = 0
    least_one_position = -1 # Tracking the index of the most recently seen '1'

    # 3. Iteration
    for i in range(len(binary_n)):
        if binary_n[i] == '1':
            # Check if a previous '1' has been found
            if least_one_position != -1:
                # Calculate relative distance
                current_distance = i - least_one_position
                max_distance = max(max_distance, current_distance)

            # Update the position of the last '1' found
            least_one_position = i

    # Return the result
    return max_distance


assert binary_gap(22) == 2, f"Input 22 failed. Expected 2, Got {binary_gap(22)}"
