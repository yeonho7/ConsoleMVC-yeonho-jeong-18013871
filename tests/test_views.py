from unittest.mock import patch
from src.models.sample import Sample
from src.models.order import Order, OrderStatus
from src.models.production_job import ProductionJob
from src.views.main_view import MainView
from src.views.sample_view import SampleView
from src.views.order_view import OrderView
from src.views.production_view import ProductionView
from src.views.monitoring_view import MonitoringView


class TestMainView:
    def setup_method(self):
        self.view = MainView()

    def test_show_header_prints_output(self, capsys):
        summary = {"sample_count": 3, "total_stock": 150, "total_orders": 5, "queue_count": 2}
        self.view.show_header(summary)
        out = capsys.readouterr().out
        assert out != ""

    def test_show_menu_prints_menu_items(self, capsys):
        self.view.show_menu()
        out = capsys.readouterr().out
        assert "0" in out

    def test_get_choice_returns_input(self):
        with patch("builtins.input", return_value="1"):
            assert self.view.get_choice() == "1"


class TestSampleView:
    def setup_method(self):
        self.view = SampleView()
        self.samples = [
            Sample(sample_id="S001", name="Alpha", avg_production_time=30.0, yield_rate=0.85),
            Sample(sample_id="S002", name="Beta", avg_production_time=20.0, yield_rate=0.90),
        ]

    def test_show_list_prints_samples(self, capsys):
        self.view.show_list(self.samples)
        out = capsys.readouterr().out
        assert "Alpha" in out
        assert "Beta" in out

    def test_show_list_empty_prints_message(self, capsys):
        self.view.show_list([])
        out = capsys.readouterr().out
        assert out != ""

    def test_show_search_result_prints_results(self, capsys):
        self.view.show_search_result(self.samples[:1])
        out = capsys.readouterr().out
        assert "Alpha" in out

    def test_show_search_result_empty_prints_message(self, capsys):
        self.view.show_search_result([])
        out = capsys.readouterr().out
        assert "없습니다" in out

    def test_input_sample_returns_dict_with_required_keys(self):
        with patch("builtins.input", side_effect=["S001", "Alpha", "30.0", "0.85"]):
            data = self.view.input_sample()
        assert "sample_id" in data
        assert "name" in data
        assert "avg_production_time" in data
        assert "yield_rate" in data

    def test_input_sample_converts_numeric_fields(self):
        with patch("builtins.input", side_effect=["S001", "Alpha", "30.0", "0.85"]):
            data = self.view.input_sample()
        assert isinstance(data["avg_production_time"], float)
        assert isinstance(data["yield_rate"], float)

    def test_show_submenu_returns_choice(self):
        with patch("builtins.input", return_value="1"):
            choice = self.view.show_submenu()
        assert choice == "1"


class TestOrderView:
    def setup_method(self):
        self.view = OrderView()
        self.orders = [
            Order(order_no="ORD-20260508-0001", sample_id="S001", customer="ACME", quantity=50),
            Order(order_no="ORD-20260508-0002", sample_id="S001", customer="Beta Corp", quantity=30),
        ]

    def test_show_reserved_list_prints_orders(self, capsys):
        self.view.show_reserved_list(self.orders)
        out = capsys.readouterr().out
        assert "ACME" in out

    def test_show_reserved_list_empty_prints_message(self, capsys):
        self.view.show_reserved_list([])
        out = capsys.readouterr().out
        assert "없습니다" in out

    def test_show_confirmed_list_prints_orders(self, capsys):
        self.view.show_confirmed_list(self.orders)
        out = capsys.readouterr().out
        assert out != ""

    def test_show_confirmed_list_empty_prints_message(self, capsys):
        self.view.show_confirmed_list([])
        out = capsys.readouterr().out
        assert "없습니다" in out

    def test_input_order_returns_dict_with_required_keys(self):
        with patch("builtins.input", side_effect=["S001", "ACME", "50"]):
            data = self.view.input_order()
        assert "sample_id" in data
        assert "customer" in data
        assert "quantity" in data

    def test_input_order_converts_quantity_to_int(self):
        with patch("builtins.input", side_effect=["S001", "ACME", "50"]):
            data = self.view.input_order()
        assert isinstance(data["quantity"], int)

    def test_show_order_result_prints_order(self, capsys):
        order = self.orders[0]
        self.view.show_order_result(order)
        out = capsys.readouterr().out
        assert order.order_no in out

    def test_get_order_choice_returns_input(self):
        with patch("builtins.input", return_value="1"):
            choice = self.view.get_order_choice(self.orders)
        assert choice == "1"


class TestProductionView:
    def setup_method(self):
        self.view = ProductionView()

    def test_show_current_with_job_prints_job_info(self, capsys):
        job = ProductionJob(order_no="ORD-1", sample_id="S001", shortage=40, actual_qty=53, total_time=1590.0)
        self.view.show_current(job)
        out = capsys.readouterr().out
        assert "ORD-1" in out

    def test_show_current_with_none_prints_message(self, capsys):
        self.view.show_current(None)
        out = capsys.readouterr().out
        assert out != ""

    def test_show_queue_empty_prints_message(self, capsys):
        self.view.show_queue([])
        out = capsys.readouterr().out
        assert out != ""

    def test_show_queue_with_jobs_prints_jobs(self, capsys):
        jobs = [ProductionJob(order_no="ORD-2", sample_id="S001", shortage=20, actual_qty=26, total_time=780.0)]
        self.view.show_queue(jobs)
        out = capsys.readouterr().out
        assert "ORD-2" in out


class TestMonitoringView:
    def setup_method(self):
        self.view = MonitoringView()

    def test_show_order_stats_prints_stats(self, capsys):
        from src.models.order import OrderStatus
        stats = {OrderStatus.RESERVED: 2, OrderStatus.CONFIRMED: 1}
        self.view.show_order_stats(stats)
        out = capsys.readouterr().out
        assert out != ""

    def test_show_inventory_prints_entries(self, capsys):
        inventory = [{"sample_id": "S001", "name": "Alpha", "stock": 50, "status": "여유"}]
        self.view.show_inventory(inventory)
        out = capsys.readouterr().out
        assert "Alpha" in out

    def test_show_inventory_empty_prints_message(self, capsys):
        self.view.show_inventory([])
        out = capsys.readouterr().out
        assert "없습니다" in out

    def test_show_submenu_returns_choice(self):
        with patch("builtins.input", return_value="1"):
            choice = self.view.show_submenu()
        assert choice == "1"
