import pytest
from src.store import InMemoryStore
from src.controllers.monitoring_controller import MonitoringController
from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.models.order import OrderStatus


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def ctrl(store):
    return MonitoringController(store)


@pytest.fixture
def setup(store):
    sc = SampleController(store)
    oc = OrderController(store)
    s1 = sc.register("S-001", "GaAs Wafer", 30.0, 0.9)
    s1.stock = 20
    s2 = sc.register("S-002", "InP Wafer", 45.0, 0.8)
    s2.stock = 0
    return sc, oc, s1, s2


class TestMonitoringControllerOrderStats:
    def test_returns_empty_stats_when_no_orders(self, ctrl):
        stats = ctrl.get_order_stats()
        assert stats.get(OrderStatus.RESERVED, 0) == 0

    def test_counts_reserved_orders(self, ctrl, store, setup):
        _, oc, _, _ = setup
        oc.reserve("S-001", "Lab A", 5)
        oc.reserve("S-001", "Lab B", 3)
        stats = ctrl.get_order_stats()
        assert stats[OrderStatus.RESERVED] == 2

    def test_counts_confirmed_orders(self, ctrl, store, setup):
        _, oc, _, _ = setup
        o = oc.reserve("S-001", "Lab A", 5)
        oc.approve(o.order_no)
        stats = ctrl.get_order_stats()
        assert stats[OrderStatus.CONFIRMED] == 1

    def test_excludes_rejected_orders_from_stats(self, ctrl, store, setup):
        _, oc, _, _ = setup
        o = oc.reserve("S-001", "Lab A", 5)
        oc.reject(o.order_no)
        stats = ctrl.get_order_stats()
        assert OrderStatus.REJECTED not in stats

    def test_counts_producing_orders(self, ctrl, store, setup):
        _, oc, _, _ = setup
        o = oc.reserve("S-002", "Lab B", 10)
        oc.approve(o.order_no)
        stats = ctrl.get_order_stats()
        assert stats[OrderStatus.PRODUCING] == 1


class TestMonitoringControllerInventoryStatus:
    def test_returns_one_entry_per_sample(self, ctrl, store, setup):
        inventory = ctrl.get_inventory_status()
        assert len(inventory) == 2

    def test_status_is_depleted_when_stock_is_zero(self, ctrl, store, setup):
        inventory = ctrl.get_inventory_status()
        s2_entry = next(e for e in inventory if e["sample_id"] == "S-002")
        assert s2_entry["status"] == "고갈"

    def test_status_is_sufficient_when_stock_covers_demand(self, ctrl, store, setup):
        # S-001: stock=20, 주문 없음 → 여유
        inventory = ctrl.get_inventory_status()
        s1_entry = next(e for e in inventory if e["sample_id"] == "S-001")
        assert s1_entry["status"] == "여유"

    def test_status_is_shortage_when_demand_exceeds_stock(self, ctrl, store, setup):
        # S-001: stock=20, RESERVED 주문 qty=25 → 부족
        _, oc, _, _ = setup
        oc.reserve("S-001", "Lab A", 25)
        inventory = ctrl.get_inventory_status()
        s1_entry = next(e for e in inventory if e["sample_id"] == "S-001")
        assert s1_entry["status"] == "부족"

    def test_shortage_check_includes_producing_orders(self, ctrl, store, setup):
        # S-001: stock=20, PRODUCING 주문 qty=25 → 부족
        _, oc, s1, _ = setup
        s1.stock = 10
        o = oc.reserve("S-001", "Lab A", 25)
        oc.approve(o.order_no)   # stock=10 < 25 → PRODUCING
        inventory = ctrl.get_inventory_status()
        s1_entry = next(e for e in inventory if e["sample_id"] == "S-001")
        assert s1_entry["status"] == "부족"

    def test_inventory_entry_includes_stock_value(self, ctrl, store, setup):
        inventory = ctrl.get_inventory_status()
        s1_entry = next(e for e in inventory if e["sample_id"] == "S-001")
        assert s1_entry["stock"] == 20
