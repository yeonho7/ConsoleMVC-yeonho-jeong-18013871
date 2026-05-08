import math
from src.store import InMemoryStore
from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.models.order import OrderStatus


class TestOrderController:
    def setup_method(self):
        self.store = InMemoryStore()
        sample_ctrl = SampleController(self.store)
        self.ctrl = OrderController(self.store)
        sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100

    def test_reserve_creates_order_in_reserved_status(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        assert order.status == OrderStatus.RESERVED

    def test_reserve_stores_order_in_store(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        assert order.order_no in self.store.orders

    def test_reserve_assigns_formatted_order_no(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        assert order.order_no.startswith("ORD-")

    def test_approve_sufficient_stock_sets_confirmed(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        approved = self.ctrl.approve(order.order_no)
        assert approved.status == OrderStatus.CONFIRMED

    def test_approve_insufficient_stock_sets_producing(self):
        self.store.samples["S001"].stock = 10
        order = self.ctrl.reserve("S001", "ACME", 50)
        approved = self.ctrl.approve(order.order_no)
        assert approved.status == OrderStatus.PRODUCING

    def test_approve_insufficient_stock_creates_current_job(self):
        self.store.samples["S001"].stock = 10
        order = self.ctrl.reserve("S001", "ACME", 50)
        self.ctrl.approve(order.order_no)
        assert self.store.current_job is not None

    def test_approve_second_insufficient_enqueues(self):
        self.store.samples["S001"].stock = 5
        order1 = self.ctrl.reserve("S001", "ACME", 50)
        order2 = self.ctrl.reserve("S001", "Beta Corp", 60)
        self.ctrl.approve(order1.order_no)
        self.ctrl.approve(order2.order_no)
        assert len(self.store.production_queue) == 1

    def test_approve_calculates_job_correctly(self):
        self.store.samples["S001"].stock = 10
        order = self.ctrl.reserve("S001", "ACME", 50)
        self.ctrl.approve(order.order_no)
        job = self.store.current_job
        shortage = 50 - 10
        actual_qty = math.ceil(shortage / (0.85 * 0.9))
        total_time = 30.0 * actual_qty
        assert job.shortage == shortage
        assert job.actual_qty == actual_qty
        assert job.total_time == total_time

    def test_reject_sets_rejected_status(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        rejected = self.ctrl.reject(order.order_no)
        assert rejected.status == OrderStatus.REJECTED

    def test_release_sets_released_status(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        self.ctrl.approve(order.order_no)
        released = self.ctrl.release(order.order_no)
        assert released.status == OrderStatus.RELEASED

    def test_release_sets_released_at(self):
        order = self.ctrl.reserve("S001", "ACME", 50)
        self.ctrl.approve(order.order_no)
        released = self.ctrl.release(order.order_no)
        assert released.released_at is not None

    def test_list_reserved_returns_only_reserved(self):
        order1 = self.ctrl.reserve("S001", "ACME", 50)
        order2 = self.ctrl.reserve("S001", "Beta Corp", 30)
        self.ctrl.approve(order1.order_no)
        result = self.ctrl.list_reserved()
        assert len(result) == 1
        assert result[0].order_no == order2.order_no

    def test_list_confirmed_returns_only_confirmed(self):
        order1 = self.ctrl.reserve("S001", "ACME", 50)
        self.ctrl.reserve("S001", "Beta Corp", 30)
        self.ctrl.approve(order1.order_no)
        result = self.ctrl.list_confirmed()
        assert len(result) == 1
        assert result[0].order_no == order1.order_no
