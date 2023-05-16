import sys
from enum import Enum
from dataclasses import dataclass
from collections import deque
import heapq
from typing import Union, Callable


@dataclass(order=True)
class User:
    user_id: str
    maker_cost: int = 0
    taker_cost: int = 0

    def __repr__(self):
        return f'{self.user_id}-{self.maker_cost}-{self.taker_cost}'


class OrderType(Enum):
    LIMIT = 1
    MARKET = 2


class OrderSide(Enum):
    BUY = 1
    SELL = 2


@dataclass
class Order:
    order_type: OrderType
    user_id: str
    side: OrderSide
    order_id: str
    quantity: int
    cancelled: bool = False
    price: int = -1

    def reduce_quantity(self, delta: int):
        self.quantity -= delta

    def __repr__(self):
        return f'{self.quantity}@{self.price}#{self.order_id}'


class SamePriceOrders:
    def __init__(self, price: int, side: OrderSide, order: Order):
        self.price = price
        self.side = side
        self.orders: deque[Order] = deque([order])

    def __lt__(self, other) -> bool:
        return self.price < other.price if self.side == OrderSide.SELL else self.price > other.price

    def _purge_cancelled_or_empty_orders(self) -> None:
        while self.orders and (self.orders[0].cancelled or self.orders[0].quantity == 0):
            self.orders.popleft()

    def get_earliest_order(self) -> Union[Order, None]:
        self._purge_cancelled_or_empty_orders()
        return self.orders[0] if self.orders else None

    def add_order(self, order: Order) -> None:
        self.orders.append(order)

    def __repr__(self):
        return ' '.join((repr(order) for order in self.orders if order.cancelled == False))


class UserManager:
    def __init__(self):
        self._users: dict[str, User] = {}

    def exist(self, user_id: str) -> bool:
        return user_id in self._users

    def add(self, user_id: str) -> None:
        if user_id in self._users:
            raise KeyError(f'{user_id} has already existed')
        self._users[user_id] = User(user_id=user_id)

    def __getitem__(self, user_id: str) -> User:
        if user_id not in self._users:
            raise KeyError(f'{user_id} is not a valid user ID')
        return self._users[user_id]

    def __iter__(self):
        yield from sorted(self._users.values())


class OrderBook:
    def __init__(self, user_manager: UserManager):
        self._buy_order_heap: list[SamePriceOrders] = []
        self._sell_order_heap: list[SamePriceOrders] = []
        self._buy_order_map: dict[int, SamePriceOrders] = {}
        self._sell_order_map: dict[int, SamePriceOrders] = {}
        self._order_id_map: dict[str, Order] = {}
        self._user_manager = user_manager

    def match_and_store(self, order: Order) -> int:
        if order.quantity <= 0:
            return 0
        if order.side == OrderSide.SELL:
            return self._match_and_store(
                order, self._buy_order_heap, self._buy_order_map, self._sell_order_heap, self._sell_order_map, lambda target_price: order.order_type == OrderType.MARKET or order.price <= target_price)
        else:
            assert (order.side == OrderSide.BUY)
            return self._match_and_store(
                order, self._sell_order_heap, self._sell_order_map, self._buy_order_heap, self._buy_order_map, lambda target_price: order.order_type == OrderType.MARKET or order.price >= target_price)

    def _match_and_store(self, order: Order, target_order_heap: list[SamePriceOrders], target_order_map: dict[int, SamePriceOrders], unmatched_order_heap: list[SamePriceOrders], unmatched_order_map: dict[int, SamePriceOrders], matching_predict: Callable[[int], bool]) -> int:
        total_cost: int = 0
        self._maintain_orders(target_order_heap, target_order_map)
        while target_order_heap and order.quantity and matching_predict(target_order_heap[0].get_earliest_order().price):
            contra_order = target_order_heap[0].get_earliest_order()
            trade_quantity = min(order.quantity, contra_order.quantity)
            cost = trade_quantity * contra_order.price
            total_cost += cost
            self._user_manager[order.user_id].taker_cost += cost
            self._user_manager[contra_order.user_id].maker_cost += cost
            # eprint(
            #     f'found a match: order:{order}, contra_order:{contra_order} with quantity: {trade_quantity} and cost: {cost}')
            order.reduce_quantity(trade_quantity)
            contra_order.reduce_quantity(trade_quantity)
            self._maintain_orders(target_order_heap, target_order_map)

        if order.order_type == OrderType.LIMIT and order.quantity:
            if order.price in unmatched_order_map:
                unmatched_order_map[order.price].add_order(order)
            else:
                unmatched_order_map[order.price] = SamePriceOrders(
                    order.price, order.side, order)
                heapq.heappush(unmatched_order_heap,
                               unmatched_order_map[order.price])

            assert (order.order_id not in self._order_id_map)
            self._order_id_map[order.order_id] = order

        return total_cost

    def _maintain_orders(self, order_heap: list[SamePriceOrders], order_map: dict[int, SamePriceOrders]):
        while order_heap and not order_heap[0].get_earliest_order():
            price = order_heap[0].price
            del order_map[price]
            heapq.heappop(order_heap)

    def cancel(self, user: User, order_id: str) -> None:
        if order_id not in self._order_id_map or self._order_id_map[order_id].user_id != user.user_id:
            return

        self._order_id_map[order_id].cancelled = True

    def dump_orders(self, side: OrderSide, output_file) -> None:
        if side == OrderSide.BUY:
            print(f'B: {OrderBook.repr_orders(self._buy_order_heap)}',
                  file=output_file)
        else:
            print(f'S: {OrderBook.repr_orders(self._sell_order_heap)}',
                  file=output_file)

    @classmethod
    def repr_orders(cls, orders: list[SamePriceOrders]) -> str:
        return ' '.join(repr(order) for order in sorted(orders))


def parse_side(field: str) -> OrderSide:
    if field == 'B':
        return OrderSide.BUY
    elif field == 'S':
        return OrderSide.SELL

    raise ValueError(f'unknown side {field}')


def main():
    user_manager = UserManager()
    order_book = OrderBook(user_manager)
    stdin_iterator = iter(sys.stdin)
    for _ in range(int(next(stdin_iterator))):
        user_id = next(stdin_iterator).rstrip()
        user_manager.add(user_id)

    for line in sys.stdin:
        fields: list[str] = line.rstrip().split(' ')
        if not fields or fields[0] == 'END':
            break

        if fields[0] == 'SUB':
            user_id = fields[2]
            if not user_manager.exist(user_id):
                continue
            if fields[1] == 'LO':
                order = Order(order_type=OrderType.LIMIT, user_id=user_id,
                              side=parse_side(fields[3]), order_id=fields[4], quantity=int(fields[5]), price=int(fields[6]))
            elif fields[1] == 'MO':
                order = Order(order_type=OrderType.MARKET, user_id=user_id,
                              side=parse_side(fields[3]), order_id=fields[4], quantity=int(fields[5]))
            else:
                raise ValueError(f'unknown order type {fields[1]}')

            # eprint(order)
            print(order_book.match_and_store(order))
        elif fields[0] == 'CXL':
            user_id = fields[1]
            if not user_manager.exist(user_id):
                continue
            order_book.cancel(user_manager[user_id], fields[2])
        else:
            raise ValueError(f'unknown order action {fields[0]}')

    order_book.dump_orders(OrderSide.BUY, sys.stdout)
    order_book.dump_orders(OrderSide.SELL, sys.stdout)
    for user_id in user_manager:
        print(user_id)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    main()
