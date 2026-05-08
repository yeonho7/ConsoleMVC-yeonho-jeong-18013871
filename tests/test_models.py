from datetime import datetime
from src.models.order import Order, OrderStatus
from src.models.sample import Sample
from src.models.production_job import ProductionJob


class TestOrderStatus:
    def test_reserved_value(self):
        assert OrderStatus.RESERVED.value == "RESERVED"

    def test_rejected_value(self):
        assert OrderStatus.REJECTED.value == "REJECTED"

    def test_producing_value(self):
        assert OrderStatus.PRODUCING.value == "PRODUCING"

    def test_confirmed_value(self):
        assert OrderStatus.CONFIRMED.value == "CONFIRMED"

    def test_released_value(self):
        assert OrderStatus.RELEASED.value == "RELEASED"


class TestOrder:
    def test_create_with_required_fields(self):
        order = Order(order_no="ORD-20260508-0001", sample_id="S001", customer="ACME", quantity=100)
        assert order.order_no == "ORD-20260508-0001"
        assert order.sample_id == "S001"
        assert order.customer == "ACME"
        assert order.quantity == 100

    def test_default_status_is_reserved(self):
        order = Order(order_no="ORD-1", sample_id="S001", customer="X", quantity=1)
        assert order.status == OrderStatus.RESERVED

    def test_created_at_defaults_to_now(self):
        before = datetime.now()
        order = Order(order_no="ORD-1", sample_id="S001", customer="X", quantity=1)
        after = datetime.now()
        assert before <= order.created_at <= after

    def test_released_at_defaults_to_none(self):
        order = Order(order_no="ORD-1", sample_id="S001", customer="X", quantity=1)
        assert order.released_at is None


class TestSample:
    def test_create_with_required_fields(self):
        sample = Sample(sample_id="S001", name="Alpha", avg_production_time=30.0, yield_rate=0.85)
        assert sample.sample_id == "S001"
        assert sample.name == "Alpha"
        assert sample.avg_production_time == 30.0
        assert sample.yield_rate == 0.85

    def test_default_stock_is_zero(self):
        sample = Sample(sample_id="S001", name="Alpha", avg_production_time=30.0, yield_rate=0.85)
        assert sample.stock == 0


class TestProductionJob:
    def test_create_with_all_fields(self):
        job = ProductionJob(order_no="ORD-1", sample_id="S001", shortage=40, actual_qty=53, total_time=1590.0)
        assert job.order_no == "ORD-1"
        assert job.sample_id == "S001"
        assert job.shortage == 40
        assert job.actual_qty == 53
        assert job.total_time == 1590.0
