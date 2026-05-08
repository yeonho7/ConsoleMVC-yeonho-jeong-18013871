import math
import pytest
from src.store import InMemoryStore
from src.controllers.order_controller import OrderController
from src.controllers.sample_controller import SampleController
from src.models.order import OrderStatus
from src.models.production_job import ProductionJob


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def sample_ctrl(store):
    return SampleController(store)


@pytest.fixture
def ctrl(store):
    return OrderController(store)


@pytest.fixture
def sample_with_stock(store, sample_ctrl):
    sample = sample_ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
    sample.stock = 20
    return sample


@pytest.fixture
def sample_no_stock(store, sample_ctrl):
    sample = sample_ctrl.register("S-002", "InP Wafer", 45.0, 0.8)
    sample.stock = 0
    return sample


class TestOrderControllerReserve:
    def test_reserve_creates_order_with_reserved_status(self, ctrl, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        assert order.status == OrderStatus.RESERVED

    def test_reserve_saves_order_to_store(self, ctrl, store, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        assert order.order_no in store.orders

    def test_reserve_assigns_order_number(self, ctrl, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        assert order.order_no.startswith("ORD-")

    def test_reserve_stores_correct_fields(self, ctrl, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        assert order.sample_id == "S-001"
        assert order.customer == "Lab A"
        assert order.quantity == 5


class TestOrderControllerApproveWithSufficientStock:
    def test_approve_sets_confirmed_when_stock_sufficient(self, ctrl, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        result = ctrl.approve(order.order_no)
        assert result.status == OrderStatus.CONFIRMED

    def test_approve_does_not_enqueue_job_when_stock_sufficient(self, ctrl, store, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        ctrl.approve(order.order_no)
        assert len(store.production_queue) == 0


class TestOrderControllerApproveWithInsufficientStock:
    def test_approve_sets_producing_when_stock_insufficient(self, ctrl, sample_no_stock):
        order = ctrl.reserve("S-002", "Lab B", 10)
        result = ctrl.approve(order.order_no)
        assert result.status == OrderStatus.PRODUCING

    def test_approve_enqueues_production_job_when_stock_insufficient(self, ctrl, store, sample_no_stock):
        order = ctrl.reserve("S-002", "Lab B", 10)
        ctrl.approve(order.order_no)
        assert len(store.production_queue) == 1

    def test_approve_calculates_shortage_correctly(self, ctrl, store, sample_no_stock):
        # stock=0, quantity=10 → shortage=10
        order = ctrl.reserve("S-002", "Lab B", 10)
        ctrl.approve(order.order_no)
        job = store.production_queue[0]
        assert job.shortage == 10

    def test_approve_calculates_actual_qty_with_formula(self, ctrl, store, sample_no_stock):
        # yield_rate=0.8, shortage=10 → ceil(10 / (0.8 * 0.9)) = ceil(13.888...) = 14
        order = ctrl.reserve("S-002", "Lab B", 10)
        ctrl.approve(order.order_no)
        job = store.production_queue[0]
        expected = math.ceil(10 / (0.8 * 0.9))
        assert job.actual_qty == expected

    def test_approve_calculates_total_time_correctly(self, ctrl, store, sample_no_stock):
        # avg_production_time=45.0, actual_qty=14 → 45.0 * 14 = 630.0
        order = ctrl.reserve("S-002", "Lab B", 10)
        ctrl.approve(order.order_no)
        job = store.production_queue[0]
        expected_qty = math.ceil(10 / (0.8 * 0.9))
        assert job.total_time == 45.0 * expected_qty

    def test_approve_production_job_linked_to_order(self, ctrl, store, sample_no_stock):
        order = ctrl.reserve("S-002", "Lab B", 10)
        ctrl.approve(order.order_no)
        job = store.production_queue[0]
        assert job.order_no == order.order_no
        assert job.sample_id == "S-002"


class TestOrderControllerReject:
    def test_reject_sets_rejected_status(self, ctrl, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        result = ctrl.reject(order.order_no)
        assert result.status == OrderStatus.REJECTED


class TestOrderControllerRelease:
    def test_release_sets_released_status(self, ctrl, sample_with_stock):
        order = ctrl.reserve("S-001", "Lab A", 5)
        ctrl.approve(order.order_no)
        result = ctrl.release(order.order_no)
        assert result.status == OrderStatus.RELEASED

    def test_release_sets_released_at_timestamp(self, ctrl, sample_with_stock):
        from datetime import datetime
        order = ctrl.reserve("S-001", "Lab A", 5)
        ctrl.approve(order.order_no)
        before = datetime.now()
        result = ctrl.release(order.order_no)
        after = datetime.now()
        assert result.released_at is not None
        assert before <= result.released_at <= after


class TestOrderControllerLists:
    def test_list_reserved_returns_only_reserved_orders(self, ctrl, sample_with_stock):
        o1 = ctrl.reserve("S-001", "Lab A", 5)
        o2 = ctrl.reserve("S-001", "Lab B", 3)
        ctrl.approve(o2.order_no)
        reserved = ctrl.list_reserved()
        assert len(reserved) == 1
        assert reserved[0].order_no == o1.order_no

    def test_list_confirmed_returns_only_confirmed_orders(self, ctrl, sample_with_stock):
        o1 = ctrl.reserve("S-001", "Lab A", 5)
        o2 = ctrl.reserve("S-001", "Lab B", 3)
        ctrl.approve(o1.order_no)
        confirmed = ctrl.list_confirmed()
        assert len(confirmed) == 1
        assert confirmed[0].order_no == o1.order_no
