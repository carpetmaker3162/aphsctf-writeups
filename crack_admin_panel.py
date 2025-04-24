# credit: ChatGPT

hash_val = 56951
B = 31
min_digit = 33
max_digit = 126
offset = 2**17

# The extra amount each digit can add beyond min_digit.
digit_extra = max_digit - min_digit  # 93

def solve_for_length(S, L, B, digit_extra):
    """
    Try to represent S = sum_{i=0}^{L-1} x[i]*B^i with 0 <= x[i] <= digit_extra.
    Returns list of x's if possible (lowest order first) or None.
    """
    # Precompute powers and maximum sums for a given number of digits.
    powers = [B**i for i in range(L)]
    # max_possible for indices 0..i is when all x = digit_extra.
    max_for = [0]*L
    s = 0
    for i in range(L):
        s += powers[i]
        max_for[i] = s * digit_extra

    # We'll solve using recursion from highest exponent to lowest.
    # x[i] corresponds to B^i, i=0 is lowest order.
    solution = [None]*L
    def backtrack(i, remaining):
        if i < 0:
            return remaining == 0
        # i is the current exponent.
        # For indices 0..i, the maximum achievable extra is max_for[i]
        if remaining > max_for[i]:
            return False
        # Try every possible value for x[i]
        for x in range(digit_extra+1):
            # Check if remaining - x*powers[i] is nonnegative.
            if remaining - x*powers[i] < 0:
                break
            solution[i] = x
            if backtrack(i-1, remaining - x*powers[i]):
                return True
        return False
    if backtrack(L-1, S):
        return solution
    else:
        return None

def find_solution():
    offsets = 0
    while True:
        modified_hash = hash_val + offsets * offset
        # Try lengths 1 to 10.
        for L in range(1, 11):
            # The minimum achievable value for L digits is:
            base_min = sum(B**i for i in range(L)) * min_digit
            base_max = sum(B**i for i in range(L)) * max_digit
            if base_min <= modified_hash <= base_max:
                # Subtract the minimum contribution to get S:
                S = modified_hash - sum(B**i for i in range(L)) * min_digit
                sol = solve_for_length(S, L, B, digit_extra)
                if sol is not None:
                    # Convert x back to coefficients:
                    coeffs = [x + min_digit for x in sol]
                    return offsets, L, coeffs
        offsets += 1

offsets, L, coeffs = find_solution()
# Build the corresponding string
s = "".join(chr(c) for c in coeffs)
print("Offsets =", offsets)
print("Length =", L)
print("Coefficients =", coeffs)
print("String =", s)

# Verify the hash:
calc_hash = sum(c * (B**i) for i, c in enumerate(coeffs))
print("Computed hash =", calc_hash)
print("Modified hash =", hash_val + offsets * offset)
