from src.store import InMemoryStore
from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.controllers.production_controller import ProductionController
from src.models.production_job import ProductionJob
from src.models.order import OrderStatus


class TestProductionController:
    def setup_method(self):
        self.store = InMemoryStore()
        sample_ctrl = SampleController(self.store)
        self.order_ctrl = OrderController(self.store)
        self.ctrl = ProductionController(self.store)
        sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 5  # 항상 부족

    def test_get_queue_empty_initially(self):
        assert self.ctrl.get_queue() == []

    def test_get_current_none_initially(self):
        assert self.ctrl.get_current() is None

    def test_enqueue_adds_job_to_queue(self):
        job = ProductionJob(order_no="ORD-1", sample_id="S001", shortage=10, actual_qty=13, total_time=390.0)
        self.ctrl.enqueue(job)
        assert len(self.store.production_queue) == 1

    def test_complete_current_returns_none_when_no_current(self):
        result = self.ctrl.complete_current()
        assert result is None

    def test_complete_current_sets_order_to_confirmed(self):
        order = self.order_ctrl.reserve("S001", "ACME", 50)
        self.order_ctrl.approve(order.order_no)
        result = self.ctrl.complete_current()
        assert result is not None
        assert result.status == OrderStatus.CONFIRMED

    def test_complete_current_advances_queue_to_next_job(self):
        order1 = self.order_ctrl.reserve("S001", "ACME", 50)
        order2 = self.order_ctrl.reserve("S001", "Beta Corp", 60)
        self.order_ctrl.approve(order1.order_no)  # current_job
        self.order_ctrl.approve(order2.order_no)  # queue
        self.ctrl.complete_current()
        assert self.store.current_job is not None
        assert self.store.current_job.order_no == order2.order_no

    def test_complete_current_clears_current_when_queue_empty(self):
        order = self.order_ctrl.reserve("S001", "ACME", 50)
        self.order_ctrl.approve(order.order_no)
        self.ctrl.complete_current()
        assert self.store.current_job is None
