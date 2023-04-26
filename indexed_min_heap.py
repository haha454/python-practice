from __future__ import annotations
from dataclasses import dataclass
import unittest


@dataclass
class Node:
    key: object
    score: int

    def __lt__(self, other: Node):
        return self.score < other.score


class IndexedMinHeap:
    def __init__(self, *args):
        self.__lst: list[Node] = []  # store scores
        self.__key_to_index_map: dict[object, int] = {}

    def __swim(self, idx: int):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.__lst[idx] < self.__lst[parent]:
                self.__swap(idx, parent)
            else:
                break
            idx = parent

    def __update_key_to_index_map(self, idx: int):
        self.__key_to_index_map[self.__lst[idx].key] = idx

    def __swap(self, idx_0: int, idx_1: int):
        self.__lst[idx_0], self.__lst[idx_1] = self.__lst[idx_1], self.__lst[idx_0]
        self.__update_key_to_index_map(idx_0)
        self.__update_key_to_index_map(idx_1)

    def __sink(self, idx: int):
        while idx * 2 + 1 < len(self.__lst):
            child = idx * 2 + 1 if idx * 2 + \
                2 == len(self.__lst) or self.__lst[idx * 2 + 1] < self.__lst[idx * 2 + 2] else idx * 2 + 2
            if self.__lst[idx] > self.__lst[child]:
                self.__swap(idx, child)
            else:
                break
            idx = child

    def insert(self, key: object, score: int):
        if key in self.__key_to_index_map:
            raise Exception('key exists')

        self.__lst.append(Node(key, score))
        self.__key_to_index_map[key] = len(self.__lst) - 1
        self.__swim(len(self.__lst) - 1)

    def pop(self) -> Node:
        if not self.__lst:
            raise Exception('heap is empty')
        if len(self.__lst) == 1:
            result = self.__lst.pop()
            del self.__key_to_index_map[result.key]
            return result

        self.__swap(0, len(self.__lst) - 1)
        result = self.__lst.pop()
        del self.__key_to_index_map[result.key]
        self.__sink(0)
        return result

    def update(self, key: object, score: int):
        if key not in self.__key_to_index_map:
            raise Exception('key does not exist')

        idx = self.__key_to_index_map[key]
        self.__lst[idx].score = score
        self.__sink(idx)
        self.__swim(idx)

    def __iter__(self):
        return iter(self.__lst)


class IndexedMinHeapTest(unittest.TestCase):
    def test_insert_duplicate(self):
        heap = IndexedMinHeap()
        heap.insert('A', 1)
        self.assertRaises(Exception, heap.insert, 'A', 100)

    def test_pop(self):
        heap = IndexedMinHeap()
        heap.insert('A', 10)
        heap.insert('B', 1)
        self.assertEqual(Node('B', 1), heap.pop())

    def test_pop_more_elements(self):
        heap = IndexedMinHeap()
        for i in range(5):
            heap.insert(chr(i + 65), 100 - i)

        self.assertEqual(Node('E', 96), heap.pop())
        self.assertEqual(Node('D', 97), heap.pop())
        self.assertEqual(Node('C', 98), heap.pop())
        self.assertEqual(Node('B', 99), heap.pop())
        self.assertEqual(Node('A', 100), heap.pop())
        self.assertRaises(Exception, heap.pop)

    def test_update_non_existent(self):
        heap = IndexedMinHeap()
        heap.insert('A', 1)
        self.assertRaises(Exception, heap.update, 'XXX', 100)

    def test_update(self):
        heap = IndexedMinHeap()
        heap.insert('A', 1)
        heap.insert('B', 2)
        heap.update('A', 100)
        self.assertEqual(Node('B', 2), heap.pop())

    def test_iter(self):
        heap = IndexedMinHeap()
        for i in range(5):
            heap.insert(chr(i + 65), 100 - i)

        self.assertListEqual([Node('E', 96), Node('D', 97), Node(
            'B', 99), Node('A', 100), Node('C', 98)], list(iter(heap)))


if __name__ == "__main__":
    unittest.main()
