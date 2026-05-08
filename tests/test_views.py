"""Views 계층 구조 테스트 — print/input 없이 반환값만 검증."""
import pytest
from io import StringIO
from unittest.mock import patch

from src.views.main_view import MainView
from src.views.sample_view import SampleView
from src.views.order_view import OrderView
from src.views.production_view import ProductionView
from src.views.monitoring_view import MonitoringView
from src.models.sample import Sample
from src.models.order import Order, OrderStatus
from src.models.production_job import ProductionJob


class TestMainView:
    def test_show_header_prints_without_error(self, capsys):
        view = MainView()
        summary = {"sample_count": 2, "total_stock": 50, "order_count": 5, "queue_count": 1}
        view.show_header(summary)
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_show_menu_prints_all_menu_items(self, capsys):
        view = MainView()
        view.show_menu()
        out = capsys.readouterr().out
        for num in ["1", "2", "3", "4", "5", "6", "0"]:
            assert num in out

    def test_get_choice_returns_user_input(self):
        view = MainView()
        with patch("builtins.input", return_value="1"):
            assert view.get_choice() == "1"


class TestSampleView:
    def test_show_list_prints_without_error(self, capsys):
        view = SampleView()
        samples = [Sample("S-001", "GaAs Wafer", 30.0, 0.9, stock=10)]
        view.show_list(samples)
        out = capsys.readouterr().out
        assert "S-001" in out

    def test_show_search_result_prints_without_error(self, capsys):
        view = SampleView()
        samples = [Sample("S-001", "GaAs Wafer", 30.0, 0.9, stock=10)]
        view.show_search_result(samples)
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_input_sample_returns_dict_with_required_keys(self):
        view = SampleView()
        responses = ["S-001", "GaAs Wafer", "30.0", "0.9"]
        with patch("builtins.input", side_effect=responses):
            result = view.input_sample()
        assert "sample_id" in result
        assert "name" in result
        assert "avg_production_time" in result
        assert "yield_rate" in result

    def test_show_submenu_prints_options(self, capsys):
        view = SampleView()
        with patch("builtins.input", return_value="1"):
            view.show_submenu()
        out = capsys.readouterr().out
        assert len(out) > 0


class TestOrderView:
    def test_show_reserved_list_prints_without_error(self, capsys):
        view = OrderView()
        orders = [Order("ORD-20260508-0001", "S-001", "Lab A", 5)]
        view.show_reserved_list(orders)
        out = capsys.readouterr().out
        assert "ORD-20260508-0001" in out

    def test_show_confirmed_list_prints_without_error(self, capsys):
        view = OrderView()
        orders = [Order("ORD-20260508-0001", "S-001", "Lab A", 5, status=OrderStatus.CONFIRMED)]
        view.show_confirmed_list(orders)
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_input_order_returns_dict_with_required_keys(self):
        view = OrderView()
        with patch("builtins.input", side_effect=["S-001", "Lab A", "5"]):
            result = view.input_order()
        assert "sample_id" in result
        assert "customer" in result
        assert "quantity" in result

    def test_show_order_result_prints_order_no(self, capsys):
        view = OrderView()
        order = Order("ORD-20260508-0001", "S-001", "Lab A", 5)
        view.show_order_result(order)
        out = capsys.readouterr().out
        assert "ORD-20260508-0001" in out

    def test_get_order_choice_returns_user_input(self):
        view = OrderView()
        orders = [Order("ORD-20260508-0001", "S-001", "Lab A", 5)]
        with patch("builtins.input", return_value="1"):
            result = view.get_order_choice(orders)
        assert result == "1"


class TestProductionView:
    def test_show_current_prints_without_error_when_none(self, capsys):
        view = ProductionView()
        view.show_current(None)
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_show_current_prints_job_info(self, capsys):
        view = ProductionView()
        job = ProductionJob("ORD-20260508-0001", "S-001", shortage=5, actual_qty=7, total_time=210.0)
        view.show_current(job)
        out = capsys.readouterr().out
        assert "ORD-20260508-0001" in out

    def test_show_queue_prints_without_error(self, capsys):
        view = ProductionView()
        jobs = [ProductionJob("ORD-20260508-0001", "S-001", shortage=5, actual_qty=7, total_time=210.0)]
        view.show_queue(jobs)
        out = capsys.readouterr().out
        assert len(out) > 0


class TestMonitoringView:
    def test_show_order_stats_prints_without_error(self, capsys):
        view = MonitoringView()
        stats = {OrderStatus.RESERVED: 2, OrderStatus.CONFIRMED: 1}
        view.show_order_stats(stats)
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_show_inventory_prints_without_error(self, capsys):
        view = MonitoringView()
        inventory = [{"sample_id": "S-001", "name": "GaAs Wafer", "stock": 20, "status": "여유"}]
        view.show_inventory(inventory)
        out = capsys.readouterr().out
        assert "S-001" in out

    def test_show_submenu_prints_options(self, capsys):
        view = MonitoringView()
        with patch("builtins.input", return_value="1"):
            view.show_submenu()
        out = capsys.readouterr().out
        assert len(out) > 0
