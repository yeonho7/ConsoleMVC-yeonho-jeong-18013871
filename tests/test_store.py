from collections import deque
from src.store import InMemoryStore


class TestInMemoryStore:
    def test_initializes_empty_collections(self):
        store = InMemoryStore()
        assert store.samples == {}
        assert store.orders == {}
        assert isinstance(store.production_queue, deque)
        assert len(store.production_queue) == 0
        assert store.current_job is None

    def test_next_order_no_format(self):
        store = InMemoryStore()
        order_no = store.next_order_no()
        parts = order_no.split("-")
        assert len(parts) == 3
        assert parts[0] == "ORD"
        assert len(parts[1]) == 8   # YYYYMMDD
        assert len(parts[2]) == 4   # 0001

    def test_next_order_no_increments(self):
        store = InMemoryStore()
        first = store.next_order_no()
        second = store.next_order_no()
        assert first.split("-")[2] == "0001"
        assert second.split("-")[2] == "0002"

    def test_next_order_no_uses_today(self):
        from datetime import date
        store = InMemoryStore()
        order_no = store.next_order_no()
        today = date.today().strftime("%Y%m%d")
        assert order_no.split("-")[1] == today
