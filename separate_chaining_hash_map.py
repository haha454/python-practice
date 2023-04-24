from __future__ import annotations
from dataclasses import dataclass
import unittest


@dataclass
class Node:
    key: object
    val: object
    next: Node = None


class SeparateChainingHashST:
    BUCKETS = 10007

    def __init__(self):
        self.__buckets = [Node(None, None)
                          for _ in range(SeparateChainingHashST.BUCKETS)]

    def __get_bucket_idx(self, key: object) -> int:
        return hash(key) & (SeparateChainingHashST.BUCKETS - 1)

    def __find(self, bucketIdx: int, key: object) -> Node:
        prv = self.__buckets[bucketIdx]
        while prv.next and prv.next.key != key:
            prv = prv.next

        return prv

    def __setitem__(self, key: object, val: object):
        if not key:
            raise Exception('key cannot be None')
        bucketIdx = self.__get_bucket_idx(key)
        prv = self.__find(bucketIdx, key)
        if prv.next:
            prv.next.val = val
        else:
            prv.next = Node(key, val)

    def __getitem__(self, key: object) -> object:
        if not key:
            raise Exception('key cannot be None')
        bucketIdx = self.__get_bucket_idx(key)
        prv = self.__find(bucketIdx, key)
        return prv.next.val if prv.next else None

    def __delitem__(self, key: object):
        if not key:
            raise Exception('key cannot be None')
        bucketIdx = self.__get_bucket_idx(key)
        prv = self.__find(bucketIdx, key)
        if prv.next == None:
            raise Exception('key does not exist')
        prv.next = prv.next.next

    def __repr__(self):
        return f'{self.__buckets}'


class TestSeparateChainingHashST(unittest.TestCase):
    def test_basic(self):
        st = SeparateChainingHashST()
        st['1'] = 1
        self.assertEqual(1, st['1'])
        self.assertIsNone(st[1])
        self.assertIsNone(st['2'])
        st['2'] = 2
        self.assertEqual(1, st['1'])
        self.assertEqual(2, st['2'])

        del st['1']
        self.assertIsNone(st['1'])
        with self.assertRaises(Exception) as exception_context:
            del st['1']

        self.assertIn('key does not exist', repr(exception_context.exception))


if __name__ == '__main__':
    unittest.main()
