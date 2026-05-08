import math
from datetime import datetime
from src.models.order import Order, OrderStatus
from src.models.production_job import ProductionJob


class OrderController:
    def __init__(self, store):
        self.store = store

    def reserve(self, sample_id: str, customer: str, quantity: int) -> Order:
        order_no = self.store.next_order_no()
        order = Order(order_no=order_no, sample_id=sample_id, customer=customer, quantity=quantity)
        self.store.orders[order_no] = order
        return order

    def approve(self, order_no: str) -> Order:
        order = self.store.orders[order_no]
        sample = self.store.samples[order.sample_id]
        if sample.stock >= order.quantity:
            order.status = OrderStatus.CONFIRMED
        else:
            shortage = order.quantity - sample.stock
            actual_qty = math.ceil(shortage / (sample.yield_rate * 0.9))
            total_time = sample.avg_production_time * actual_qty
            job = ProductionJob(
                order_no=order_no,
                sample_id=order.sample_id,
                shortage=shortage,
                actual_qty=actual_qty,
                total_time=total_time,
            )
            if self.store.current_job is None:
                self.store.current_job = job
            else:
                self.store.production_queue.append(job)
            order.status = OrderStatus.PRODUCING
        return order

    def reject(self, order_no: str) -> Order:
        order = self.store.orders[order_no]
        order.status = OrderStatus.REJECTED
        return order

    def release(self, order_no: str) -> Order:
        order = self.store.orders[order_no]
        order.status = OrderStatus.RELEASED
        order.released_at = datetime.now()
        return order

    def list_reserved(self) -> list[Order]:
        return [o for o in self.store.orders.values() if o.status == OrderStatus.RESERVED]

    def list_confirmed(self) -> list[Order]:
        return [o for o in self.store.orders.values() if o.status == OrderStatus.CONFIRMED]
