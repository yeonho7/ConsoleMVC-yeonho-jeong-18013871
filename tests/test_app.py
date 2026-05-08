from unittest.mock import patch, MagicMock
from src.store import InMemoryStore
from src.app import App


class TestApp:
    def setup_method(self):
        self.store = InMemoryStore()
        self.app = App(self.store)

    def test_app_initializes_all_controllers(self):
        assert self.app.sample_ctrl is not None
        assert self.app.order_ctrl is not None
        assert self.app.production_ctrl is not None
        assert self.app.monitoring_ctrl is not None

    def test_app_initializes_all_views(self):
        assert self.app.main_view is not None
        assert self.app.sample_view is not None
        assert self.app.order_view is not None
        assert self.app.production_view is not None
        assert self.app.monitoring_view is not None

    def test_get_summary_returns_required_keys(self):
        summary = self.app._get_summary()
        assert "sample_count" in summary
        assert "total_stock" in summary
        assert "total_orders" in summary
        assert "queue_count" in summary

    def test_get_summary_empty_store(self):
        summary = self.app._get_summary()
        assert summary["sample_count"] == 0
        assert summary["total_stock"] == 0
        assert summary["total_orders"] == 0
        assert summary["queue_count"] == 0

    def test_run_exits_on_choice_zero(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", return_value="0"):
            self.app.run()  # should return without infinite loop
