from datetime import datetime
from src.models.order import Order, OrderStatus
from src.models.sample import Sample
from src.models.production_job import ProductionJob


class TestOrderStatus:
    def test_has_all_five_statuses(self):
        assert OrderStatus.RESERVED
        assert OrderStatus.REJECTED
        assert OrderStatus.PRODUCING
        assert OrderStatus.CONFIRMED
        assert OrderStatus.RELEASED


class TestOrder:
    def test_creates_with_required_fields(self):
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=10)
        assert order.order_no == "ORD-20260508-0001"
        assert order.sample_id == "S-001"
        assert order.customer == "Lab A"
        assert order.quantity == 10

    def test_default_status_is_reserved(self):
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=10)
        assert order.status == OrderStatus.RESERVED

    def test_default_released_at_is_none(self):
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=10)
        assert order.released_at is None

    def test_created_at_is_set_automatically(self):
        before = datetime.now()
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=10)
        after = datetime.now()
        assert before <= order.created_at <= after


class TestSample:
    def test_creates_with_required_fields(self):
        sample = Sample(sample_id="S-001", name="GaAs Wafer", avg_production_time=30.0, yield_rate=0.9)
        assert sample.sample_id == "S-001"
        assert sample.name == "GaAs Wafer"
        assert sample.avg_production_time == 30.0
        assert sample.yield_rate == 0.9

    def test_default_stock_is_zero(self):
        sample = Sample(sample_id="S-001", name="GaAs Wafer", avg_production_time=30.0, yield_rate=0.9)
        assert sample.stock == 0


class TestProductionJob:
    def test_creates_with_all_fields(self):
        job = ProductionJob(order_no="ORD-20260508-0001", sample_id="S-001", shortage=5, actual_qty=7, total_time=210.0)
        assert job.order_no == "ORD-20260508-0001"
        assert job.sample_id == "S-001"
        assert job.shortage == 5
        assert job.actual_qty == 7
        assert job.total_time == 210.0
