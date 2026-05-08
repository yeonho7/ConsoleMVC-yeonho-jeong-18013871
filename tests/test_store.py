import re
from src.store import InMemoryStore


class TestInMemoryStore:
    def test_init_samples_empty(self):
        store = InMemoryStore()
        assert store.samples == {}

    def test_init_orders_empty(self):
        store = InMemoryStore()
        assert store.orders == {}

    def test_init_production_queue_empty(self):
        store = InMemoryStore()
        assert len(store.production_queue) == 0

    def test_init_current_job_is_none(self):
        store = InMemoryStore()
        assert store.current_job is None

    def test_next_order_no_matches_format(self):
        store = InMemoryStore()
        order_no = store.next_order_no()
        assert re.match(r"ORD-\d{8}-\d{4}", order_no)

    def test_next_order_no_starts_at_0001(self):
        store = InMemoryStore()
        assert store.next_order_no().endswith("0001")

    def test_next_order_no_increments(self):
        store = InMemoryStore()
        first = store.next_order_no()
        second = store.next_order_no()
        assert first.endswith("0001")
        assert second.endswith("0002")
        assert first != second
