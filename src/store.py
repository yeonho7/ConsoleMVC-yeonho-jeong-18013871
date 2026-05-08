from collections import deque
from datetime import date
from src.models.sample import Sample
from src.models.order import Order
from src.models.production_job import ProductionJob


class InMemoryStore:
    def __init__(self):
        self.samples: dict[str, Sample] = {}
        self.orders: dict[str, Order] = {}
        self.production_queue: deque[ProductionJob] = deque()
        self.current_job: ProductionJob | None = None
        self._order_counter: int = 0

    def next_order_no(self) -> str:
        self._order_counter += 1
        today = date.today().strftime("%Y%m%d")
        return f"ORD-{today}-{self._order_counter:04d}"
