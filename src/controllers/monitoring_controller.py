from src.models.order import OrderStatus


class MonitoringController:
    def __init__(self, store):
        self.store = store

    def get_order_stats(self) -> dict:
        stats = {s: 0 for s in OrderStatus if s != OrderStatus.REJECTED}
        for order in self.store.orders.values():
            if order.status != OrderStatus.REJECTED:
                stats[order.status] += 1
        return stats

    def get_inventory_status(self) -> list[dict]:
        result = []
        for sample_id, sample in self.store.samples.items():
            active_qty = sum(
                o.quantity for o in self.store.orders.values()
                if o.sample_id == sample_id and o.status in (OrderStatus.RESERVED, OrderStatus.PRODUCING)
            )
            if sample.stock == 0:
                status = "고갈"
            elif active_qty > sample.stock:
                status = "부족"
            else:
                status = "여유"
            result.append({
                "sample_id": sample_id,
                "name": sample.name,
                "stock": sample.stock,
                "status": status,
            })
        return result
