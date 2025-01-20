def max_diff(tuples):
    return max(b - a for a, b in tuples)


def max_difference(test_list):
    return max(abs(a - b) for a, b in test_list)


print(max_diff([[3, 5], [1, 7], [10, 3], [1, 2]]))  # 4
