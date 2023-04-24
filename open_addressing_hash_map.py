from dataclasses import dataclass
import functools


@dataclass
class Node:
    key: object
    val: object
    deleted: bool = False


class LinearProbingHashST:
    def __init__(self, bucket_size: int):
        self.__nodes: list[Node] = [None for i in range(bucket_size)]

    def __find(self, key: object) -> int:
        init_bucket_idx = hash(key) & (len(self.__nodes) - 1)
        for i in range(len(self.__nodes)):
            nxt_bucket_idx = (init_bucket_idx + i) & (len(self.__nodes) - 1)
            if self.__nodes[nxt_bucket_idx] == None or self.__nodes[nxt_bucket_idx].key == key:
                return nxt_bucket_idx

        return -1

    def __setitem__(self, key: object, val: object) -> bool:
        resulted_bucket_idx = self.__find(key)
        if resulted_bucket_idx == -1:
            raise Exception('hash table is full')
        else:
            if self.__nodes[resulted_bucket_idx]:
                self.__nodes[resulted_bucket_idx].val = val
                self.__nodes[resulted_bucket_idx].deleted = False
            else:
                self.__nodes[resulted_bucket_idx] = Node(key, val)

    def __getitem__(self, key: object) -> object:
        resulted_bucket_idx = self.__find(key)
        if resulted_bucket_idx == -1 or self.__nodes[resulted_bucket_idx] == None or self.__nodes[resulted_bucket_idx].deleted:
            return None
        return self.__nodes[resulted_bucket_idx].val

    def __delitem__(self, key: object) -> object:
        resulted_bucket_idx = self.__find(key)
        if resulted_bucket_idx == -1 or self.__nodes[resulted_bucket_idx] == None or self.__nodes[resulted_bucket_idx].deleted:
            raise Exception('key not found')
        self.__nodes[resulted_bucket_idx].deleted = True

    def __repr__(self):
        return f'{[node for node in self.__nodes]}'

    def items(self):
        return ((node.key, node.val) for node in self.__nodes if node and not node.deleted)


class ResizableOpenAddressingHashST:
    INIT_HASH_TABLE_SIZE = 4

    def __init__(self):
        self.__cur_size: int = ResizableOpenAddressingHashST.INIT_HASH_TABLE_SIZE
        self.__table: LinearProbingHashST = LinearProbingHashST(
            self.__cur_size)

    def __getitem__(self, key: object) -> object:
        return self.__table[key]

    @staticmethod
    def __print_upon_exit(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            func(self, *args, **kwargs)
            print(self)

        return wrapped_func

    @__print_upon_exit
    def __setitem__(self, key: object, val: object):
        try:
            self.__table[key] = val
        except Exception as ex:
            print(ex, 'resizing...')
            self.__cur_size *= 2
            new_table = LinearProbingHashST(self.__cur_size)
            for original_table_key, original_table_val in self.__table.items():
                new_table[original_table_key] = original_table_val
            new_table[key] = val
            self.__table = new_table

    @__print_upon_exit
    def __delitem__(self, key):
        del self.__table[key]

    def __repr__(self):
        return f'{self.__cur_size} {self.__table}'


if __name__ == '__main__':
    st = ResizableOpenAddressingHashST()
    st[0] = 100
    st[4] = 101
    st[8] = 102
    st[12] = 103
    st[16] = 104
    del st[16]
    st[16] = 104
    del st[16]
    st[16] = 104
    del st[16]
    st[16] = 104
    del st[16]
    print(st[16])
