from src.models.order import Order, OrderStatus
from src.models.production_job import ProductionJob
from src.store import InMemoryStore


class ProductionController:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def get_current(self) -> ProductionJob | None:
        return self._store.current_job

    def get_queue(self) -> list[ProductionJob]:
        return list(self._store.production_queue)

    def complete_current(self) -> Order | None:
        job = self._store.current_job
        if job is None:
            return None

        order = self._store.orders[job.order_no]
        order.status = OrderStatus.CONFIRMED

        if self._store.production_queue:
            self._store.current_job = self._store.production_queue.popleft()
        else:
            self._store.current_job = None

        return order
