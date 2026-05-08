from src.models.order import Order, OrderStatus
from src.models.production_job import ProductionJob


class ProductionController:
    def __init__(self, store):
        self.store = store

    def enqueue(self, job: ProductionJob) -> ProductionJob:
        self.store.production_queue.append(job)
        return job

    def complete_current(self) -> Order | None:
        if self.store.current_job is None:
            return None
        job = self.store.current_job
        order = self.store.orders[job.order_no]
        order.status = OrderStatus.CONFIRMED
        self.store.current_job = self.store.production_queue.popleft() if self.store.production_queue else None
        return order

    def get_current(self) -> ProductionJob | None:
        return self.store.current_job

    def get_queue(self) -> list[ProductionJob]:
        return list(self.store.production_queue)
