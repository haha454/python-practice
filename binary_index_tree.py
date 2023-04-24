import unittest
from itertools import accumulate


class BIT:
    def __init__(self, n):
        self.n: int = n
        # self.sum[<blah>100] = a[<blah>000] + a[<blah>001] + a[<blah>010] + a[<blah>011]
        self.sum: list[int] = [0 for i in range(n + 1)]

    def update(self, idx: int, delta: int):
        if idx >= self.n:
            raise Exception("out of range")
        idx += 1
        while idx <= self.n:
            self.sum[idx] += delta
            # find the right-most set bit, set the first unset bit to its left, and unset all set bits to the newly set bit's right, e.g., 0001->0010, 0011->0100, 0110->1000
            idx += idx & (-idx)

    def get_sum(self, idx: int) -> int:
        """
        idx is exclusive, i.e., returns sum(a[:idx])
        """
        if idx > self.n:
            raise Exception("out of range")
        result = 0
        while idx > 0:
            result += self.sum[idx]
            idx &= idx - 1  # unset the last set bit

        return result


class TestingBit(unittest.TestCase):
    def test_basic(self):
        arr: list[int] = [1, 2, 3, 4, 5, 6, 7, 8]
        expected_sums: list[int] = [0]
        expected_sums.extend(accumulate(arr))
        bit = BIT(len(arr))
        for idx, num in enumerate(arr):
            bit.update(idx, num)
        for first_n, expected_sum in enumerate(expected_sums):
            self.assertEqual(expected_sum, bit.get_sum(first_n))


if __name__ == '__main__':
    unittest.main()