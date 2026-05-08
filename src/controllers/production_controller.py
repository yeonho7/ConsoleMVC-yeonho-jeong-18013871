import math

from src.models.order import Order, OrderStatus
from src.models.production_job import ProductionJob
from src.store import InMemoryStore


class ProductionController:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def enqueue(self, order_no: str) -> ProductionJob:
        order = self._store.orders[order_no]
        sample = self._store.samples[order.sample_id]

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

        if self._store.current_job is None:
            self._store.current_job = job
        else:
            self._store.production_queue.append(job)

        return job

    def get_current(self) -> ProductionJob | None:
        return self._store.current_job

    def get_queue(self) -> list[ProductionJob]:
        return list(self._store.production_queue)

    def complete_current(self) -> Order | None:
        job = self._store.current_job
        if job is None:
            return None

        sample = self._store.samples[job.sample_id]
        sample.stock += job.actual_qty

        order = self._store.orders[job.order_no]
        order.status = OrderStatus.CONFIRMED

        if self._store.production_queue:
            self._store.current_job = self._store.production_queue.popleft()
        else:
            self._store.current_job = None

        return order
