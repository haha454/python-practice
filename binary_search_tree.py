from __future__ import annotations
from dataclasses import dataclass
import sys
import unittest


@dataclass
class Node:
    key: object
    val: object
    left: Node = None
    right: Node = None


class SmallestDummy:
    def __gt__(self, other: object):
        return False


class BinarySearchTree:
    def __init__(self):
        self._sentry = Node(SmallestDummy(), None)

    def insert(self, key: object, val: object) -> bool:
        """
        True if insertion succeeds; otherwise False, indicating the key has already existed in the tree.
        """
        cur = self._sentry
        while True:
            if cur.key == key:
                return False
            if key < cur.key:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = Node(key, val)
                    return True
            else:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = Node(key, val)
                    return True

    def __replace_node(self, target: Node, child: Node, new_child: Node):
        if target.left is child:
            target.left = new_child
        else:
            target.right = new_child

    def delete(self, key: object):
        pre = self._sentry
        cur = self._sentry.right
        while cur and cur.key != key:
            pre = cur
            if key < cur.key:
                cur = cur.left
            else:
                cur = cur.right

        if not cur:
            raise Exception(f'cannot find {key}')

        if not cur.left:
            self.__replace_node(pre, cur, cur.right)
        elif not cur.right:
            self.__replace_node(pre, cur, cur.left)
        else:
            # left rotate
            max_smaller_node = cur.left
            while max_smaller_node.right:
                max_smaller_node = max_smaller_node.right
            max_smaller_node.right = cur.right.left
            cur.right.left = cur.left
            cur.left = None
            self.__replace_node(pre, cur, cur.right)
            cur.right = None

    def find(self, key: object) -> object:
        cur = self._sentry.right
        while cur and cur.key != key:
            if key < cur.key:
                cur = cur.left
            else:
                cur = cur.right

        return None if not cur else cur.val

    def __iter__(self):
        cur = self._sentry.right
        while cur:
            if not cur.left:
                yield (cur.key, cur.val)
                cur = cur.right
            else:
                temp = cur.left
                while temp.right and temp.right != cur:
                    temp = temp.right

                if not temp.right:
                    temp.right = cur
                    cur = cur.left
                else:  # left subtree of cur has already been traversed
                    temp.right = None
                    yield (cur.key, cur.val)
                    cur = cur.right


class BstTest(unittest.TestCase):
    def test_insert(self):
        bst = BinarySearchTree()
        self.assertTrue(bst.insert(1, 'A'))
        self.assertFalse(bst.insert(1, 'A'))
        self.assertTrue(bst.insert(2, 'B'))
        self.assertFalse(bst.insert(2, 'B'))

    def test_iter(self):
        bst = BinarySearchTree()
        for i, j in zip(range(4), range(7, 11)):
            bst.insert(i, chr(i + 65))
            bst.insert(j, chr(j + 65))

        self.assertListEqual([(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'),
                             (7, 'H'), (8, 'I'), (9, 'J'), (10, 'K')], list(iter(bst)))

    def test_delete_exists_1(self):
        bst = BinarySearchTree()
        bst.insert(1, 'B')
        bst.insert(0, 'A')
        bst.insert(2, 'C')
        bst.delete(1)
        self.assertListEqual([(0, 'A'), (2, 'C')], list(iter(bst)))

    def test_delete_exists_2(self):
        bst = BinarySearchTree()
        for i, j in zip(range(4), range(7, 11)):
            bst.insert(i, chr(i + 65))
            bst.insert(j, chr(j + 65))

        bst.delete(2)
        bst.delete(0)
        bst.delete(10)

        self.assertListEqual([(1, 'B'), (3, 'D'), (7, 'H'), (8, 'I'), (9, 'J')], list(iter(bst)))
        
    def test_delete_non_existent(self):
        bst = BinarySearchTree()
        bst.insert(1, 'B')
        bst.insert(0, 'A')
        bst.insert(2, 'C')
        self.assertRaises(Exception, bst.delete, 4)
        
    def test_find_exists(self):
        bst = BinarySearchTree()
        bst.insert(1, 'B')
        bst.insert(0, 'A')
        bst.insert(2, 'C')
        self.assertEqual('C', bst.find(2))

    def test_find_non_existent(self):
        bst = BinarySearchTree()
        bst.insert(1, 'B')
        bst.insert(0, 'A')
        bst.insert(2, 'C')
        self.assertIsNone(bst.find(3))


if __name__ == "__main__":
    unittest.main()
