import math
import pytest
from src.store import InMemoryStore
from src.controllers.production_controller import ProductionController
from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.models.order import OrderStatus


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def ctrl(store):
    return ProductionController(store)


@pytest.fixture
def order_ctrl(store, ctrl):
    sc = SampleController(store)
    sample = sc.register("S-001", "GaAs Wafer", 30.0, 0.9)
    sample.stock = 0
    return OrderController(store, ctrl)


@pytest.fixture
def producing_order(order_ctrl, store):
    order = order_ctrl.reserve("S-001", "Lab A", 10)
    order_ctrl.approve(order.order_no)
    return order


class TestProductionControllerEnqueue:
    def test_first_enqueue_sets_current_job(self, ctrl, store, producing_order):
        assert store.current_job is not None
        assert store.current_job.order_no == producing_order.order_no

    def test_first_enqueue_leaves_queue_empty(self, ctrl, store, producing_order):
        assert len(store.production_queue) == 0

    def test_second_enqueue_goes_to_queue(self, ctrl, store, order_ctrl):
        order1 = order_ctrl.reserve("S-001", "Lab A", 10)
        order_ctrl.approve(order1.order_no)
        order2 = order_ctrl.reserve("S-001", "Lab B", 5)
        order_ctrl.approve(order2.order_no)
        assert store.current_job.order_no == order1.order_no
        assert len(store.production_queue) == 1
        assert store.production_queue[0].order_no == order2.order_no

    def test_enqueue_calculates_shortage(self, ctrl, store, producing_order):
        # stock=0, quantity=10 → shortage=10
        assert store.current_job.shortage == 10

    def test_enqueue_calculates_actual_qty_with_formula(self, ctrl, store, producing_order):
        # yield_rate=0.9, shortage=10 → ceil(10 / (0.9 * 0.9)) = ceil(12.345...) = 13
        expected = math.ceil(10 / (0.9 * 0.9))
        assert store.current_job.actual_qty == expected

    def test_enqueue_calculates_total_time(self, ctrl, store, producing_order):
        expected_qty = math.ceil(10 / (0.9 * 0.9))
        assert store.current_job.total_time == 30.0 * expected_qty

    def test_enqueue_links_job_to_order_and_sample(self, ctrl, store, producing_order):
        assert store.current_job.order_no == producing_order.order_no
        assert store.current_job.sample_id == "S-001"


class TestProductionControllerGetCurrent:
    def test_get_current_returns_none_initially(self, ctrl):
        assert ctrl.get_current() is None

    def test_get_current_returns_current_job_after_enqueue(self, ctrl, store, producing_order):
        assert ctrl.get_current() is not None
        assert ctrl.get_current().order_no == producing_order.order_no


class TestProductionControllerGetQueue:
    def test_get_queue_returns_empty_initially(self, ctrl):
        assert ctrl.get_queue() == []

    def test_get_queue_returns_waiting_jobs_only(self, ctrl, store, order_ctrl):
        order1 = order_ctrl.reserve("S-001", "Lab A", 10)
        order_ctrl.approve(order1.order_no)
        order2 = order_ctrl.reserve("S-001", "Lab B", 5)
        order_ctrl.approve(order2.order_no)
        # order1 → current_job, order2 → queue
        queue = ctrl.get_queue()
        assert len(queue) == 1
        assert queue[0].order_no == order2.order_no


class TestProductionControllerCompleteCurrentNoJob:
    def test_complete_current_returns_none_when_no_current_job(self, ctrl):
        assert ctrl.complete_current() is None


class TestProductionControllerCompleteCurrent:
    def test_complete_current_sets_order_to_confirmed(self, ctrl, store, producing_order):
        ctrl.complete_current()
        assert store.orders[producing_order.order_no].status == OrderStatus.CONFIRMED

    def test_complete_current_restores_sample_stock(self, ctrl, store, producing_order):
        job = store.current_job
        ctrl.complete_current()
        assert store.samples["S-001"].stock == job.actual_qty

    def test_complete_current_clears_current_when_queue_empty(self, ctrl, store, producing_order):
        ctrl.complete_current()
        assert store.current_job is None

    def test_complete_current_picks_next_job_from_queue(self, ctrl, store, order_ctrl):
        order1 = order_ctrl.reserve("S-001", "Lab A", 10)
        order_ctrl.approve(order1.order_no)
        order2 = order_ctrl.reserve("S-001", "Lab B", 5)
        order_ctrl.approve(order2.order_no)
        # order1 → current_job, order2 → queue
        ctrl.complete_current()
        assert store.current_job is not None
        assert store.current_job.order_no == order2.order_no
