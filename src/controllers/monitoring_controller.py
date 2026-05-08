from src.models.order import OrderStatus
from src.store import InMemoryStore


class MonitoringController:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def get_order_stats(self) -> dict:
        stats = {}
        for order in self._store.orders.values():
            if order.status == OrderStatus.REJECTED:
                continue
            stats[order.status] = stats.get(order.status, 0) + 1
        return stats

    def get_inventory_status(self) -> list[dict]:
        result = []
        for sample in self._store.samples.values():
            demand = sum(
                o.quantity
                for o in self._store.orders.values()
                if o.sample_id == sample.sample_id
                and o.status in (OrderStatus.RESERVED, OrderStatus.PRODUCING)
            )

            if sample.stock == 0:
                status = "고갈"
            elif demand > sample.stock:
                status = "부족"
            else:
                status = "여유"

            result.append({"sample_id": sample.sample_id, "name": sample.name, "stock": sample.stock, "status": status})
        return result
