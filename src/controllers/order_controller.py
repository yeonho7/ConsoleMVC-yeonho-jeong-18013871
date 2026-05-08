from datetime import datetime

from src.models.order import Order, OrderStatus
from src.store import InMemoryStore


class OrderController:
    def __init__(self, store: InMemoryStore, production_ctrl):
        self._store = store
        self._production_ctrl = production_ctrl

    def reserve(self, sample_id: str, customer: str, quantity: int) -> Order:
        order_no = self._store.next_order_no()
        order = Order(order_no=order_no, sample_id=sample_id, customer=customer, quantity=quantity)
        self._store.orders[order_no] = order
        return order

    def approve(self, order_no: str) -> Order:
        order = self._store.orders[order_no]
        sample = self._store.samples[order.sample_id]

        if sample.stock >= order.quantity:
            order.status = OrderStatus.CONFIRMED
        else:
            self._production_ctrl.enqueue(order_no)
            order.status = OrderStatus.PRODUCING

        return order

    def reject(self, order_no: str) -> Order:
        order = self._store.orders[order_no]
        order.status = OrderStatus.REJECTED
        return order

    def release(self, order_no: str) -> Order:
        order = self._store.orders[order_no]
        order.status = OrderStatus.RELEASED
        order.released_at = datetime.now()
        return order

    def list_reserved(self) -> list[Order]:
        return [o for o in self._store.orders.values() if o.status == OrderStatus.RESERVED]

    def list_confirmed(self) -> list[Order]:
        return [o for o in self._store.orders.values() if o.status == OrderStatus.CONFIRMED]
