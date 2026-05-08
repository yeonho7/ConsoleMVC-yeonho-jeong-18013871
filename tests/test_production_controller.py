import pytest
from src.store import InMemoryStore
from src.controllers.production_controller import ProductionController
from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.models.order import OrderStatus
from src.models.production_job import ProductionJob


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def ctrl(store):
    return ProductionController(store)


@pytest.fixture
def order_ctrl(store):
    sc = SampleController(store)
    sample = sc.register("S-001", "GaAs Wafer", 30.0, 0.9)
    sample.stock = 0
    return OrderController(store)


@pytest.fixture
def producing_order(order_ctrl, store):
    order = order_ctrl.reserve("S-001", "Lab A", 10)
    order_ctrl.approve(order.order_no)
    return order


class TestProductionControllerGetCurrent:
    def test_get_current_returns_none_initially(self, ctrl):
        assert ctrl.get_current() is None


class TestProductionControllerGetQueue:
    def test_get_queue_returns_empty_initially(self, ctrl):
        assert ctrl.get_queue() == []

    def test_get_queue_reflects_production_queue(self, ctrl, store, producing_order):
        queue = ctrl.get_queue()
        assert len(queue) == 1
        assert queue[0].order_no == producing_order.order_no


class TestProductionControllerCompleteCurrentNoJob:
    def test_complete_current_returns_none_when_no_current_job(self, ctrl):
        assert ctrl.complete_current() is None


class TestProductionControllerCompleteCurrent:
    def test_complete_current_moves_queue_head_to_current(self, ctrl, store, producing_order):
        # 큐에 job이 있을 때 complete_current() 호출하면 다음 job이 current가 됨
        # 먼저 current_job을 수동으로 설정 (큐에서 꺼내서)
        store.current_job = store.production_queue.popleft()
        result = ctrl.complete_current()
        assert result is not None
        assert result.status == OrderStatus.CONFIRMED

    def test_complete_current_sets_order_to_confirmed(self, ctrl, store, producing_order):
        store.current_job = store.production_queue.popleft()
        ctrl.complete_current()
        order = store.orders[producing_order.order_no]
        assert order.status == OrderStatus.CONFIRMED

    def test_complete_current_picks_next_job_from_queue(self, ctrl, store, order_ctrl):
        # 두 주문 모두 승인 → 큐에 2개 job 생성
        order1 = order_ctrl.reserve("S-001", "Lab A", 10)
        order_ctrl.approve(order1.order_no)
        order2 = order_ctrl.reserve("S-001", "Lab B", 5)
        order_ctrl.approve(order2.order_no)

        # 첫 번째를 current로 설정
        store.current_job = store.production_queue.popleft()
        ctrl.complete_current()

        # 두 번째 job이 current가 됨
        assert store.current_job is not None
        assert store.current_job.order_no == order2.order_no

    def test_complete_current_clears_current_when_queue_empty(self, ctrl, store, producing_order):
        store.current_job = store.production_queue.popleft()
        ctrl.complete_current()
        assert store.current_job is None
