from src.store import InMemoryStore
from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.controllers.monitoring_controller import MonitoringController
from src.models.order import OrderStatus


class TestMonitoringController:
    def setup_method(self):
        self.store = InMemoryStore()
        self.sample_ctrl = SampleController(self.store)
        self.order_ctrl = OrderController(self.store)
        self.ctrl = MonitoringController(self.store)

    def test_get_order_stats_empty_store(self):
        stats = self.ctrl.get_order_stats()
        assert isinstance(stats, dict)
        assert all(v == 0 for v in stats.values())

    def test_get_order_stats_counts_by_status(self):
        self.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        order1 = self.order_ctrl.reserve("S001", "ACME", 50)
        order2 = self.order_ctrl.reserve("S001", "Beta Corp", 30)
        self.order_ctrl.approve(order1.order_no)  # CONFIRMED
        stats = self.ctrl.get_order_stats()
        assert stats[OrderStatus.RESERVED] == 1
        assert stats[OrderStatus.CONFIRMED] == 1

    def test_get_order_stats_excludes_rejected(self):
        self.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        order = self.order_ctrl.reserve("S001", "ACME", 50)
        self.order_ctrl.reject(order.order_no)
        stats = self.ctrl.get_order_stats()
        assert OrderStatus.REJECTED not in stats

    def test_get_inventory_status_no_samples(self):
        result = self.ctrl.get_inventory_status()
        assert result == []

    def test_get_inventory_status_abundant(self):
        self.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        result = self.ctrl.get_inventory_status()
        assert len(result) == 1
        assert result[0]["status"] == "여유"

    def test_get_inventory_status_depleted(self):
        self.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 0
        result = self.ctrl.get_inventory_status()
        assert result[0]["status"] == "고갈"

    def test_get_inventory_status_shortage(self):
        self.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 10
        order = self.order_ctrl.reserve("S001", "ACME", 50)
        result = self.ctrl.get_inventory_status()
        assert result[0]["status"] == "부족"

    def test_get_inventory_status_has_required_fields(self):
        self.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 50
        result = self.ctrl.get_inventory_status()
        entry = result[0]
        assert "sample_id" in entry
        assert "name" in entry
        assert "stock" in entry
        assert "status" in entry
