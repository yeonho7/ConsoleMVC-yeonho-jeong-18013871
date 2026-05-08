from unittest.mock import patch, call
from src.store import InMemoryStore
from src.app import App
from src.models.order import OrderStatus


class TestApp:
    def setup_method(self):
        self.store = InMemoryStore()
        self.app = App(self.store)

    # ── 초기화 ──────────────────────────────────────────────
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

    # ── _get_summary ─────────────────────────────────────────
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

    # ── run() 라우팅 ─────────────────────────────────────────
    def test_run_exits_on_choice_zero(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", return_value="0"):
            self.app.run()

    def test_run_routes_choice_1_to_handle_sample(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", side_effect=["1", "0"]), \
             patch.object(self.app, "_handle_sample") as mock:
            self.app.run()
        mock.assert_called_once()

    def test_run_routes_choice_2_to_handle_order_reserve(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", side_effect=["2", "0"]), \
             patch.object(self.app, "_handle_order_reserve") as mock:
            self.app.run()
        mock.assert_called_once()

    def test_run_routes_choice_3_to_handle_order_approve(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", side_effect=["3", "0"]), \
             patch.object(self.app, "_handle_order_approve") as mock:
            self.app.run()
        mock.assert_called_once()

    def test_run_routes_choice_4_to_handle_monitoring(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", side_effect=["4", "0"]), \
             patch.object(self.app, "_handle_monitoring") as mock:
            self.app.run()
        mock.assert_called_once()

    def test_run_routes_choice_5_to_handle_production(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", side_effect=["5", "0"]), \
             patch.object(self.app, "_handle_production") as mock:
            self.app.run()
        mock.assert_called_once()

    def test_run_routes_choice_6_to_handle_release(self):
        with patch.object(self.app.main_view, "show_header"), \
             patch.object(self.app.main_view, "show_menu"), \
             patch.object(self.app.main_view, "get_choice", side_effect=["6", "0"]), \
             patch.object(self.app, "_handle_release") as mock:
            self.app.run()
        mock.assert_called_once()

    # ── _handle_sample ───────────────────────────────────────
    def test_handle_sample_exits_on_zero(self):
        with patch.object(self.app.sample_view, "show_submenu", return_value="0"):
            self.app._handle_sample()

    def test_handle_sample_shows_list(self):
        with patch.object(self.app.sample_view, "show_submenu", side_effect=["1", "0"]), \
             patch.object(self.app.sample_view, "show_list") as mock_show:
            self.app._handle_sample()
        mock_show.assert_called_once()

    def test_handle_sample_registers_sample(self):
        with patch.object(self.app.sample_view, "show_submenu", side_effect=["2", "0"]), \
             patch.object(self.app.sample_view, "input_sample", return_value={
                 "sample_id": "S001", "name": "Alpha",
                 "avg_production_time": 30.0, "yield_rate": 0.85,
             }), \
             patch("builtins.print"):
            self.app._handle_sample()
        assert "S001" in self.store.samples

    def test_handle_sample_searches_by_keyword(self):
        self.app.sample_ctrl.register("S001", "Alpha Chip", 30.0, 0.85)
        with patch.object(self.app.sample_view, "show_submenu", side_effect=["3", "0"]), \
             patch("builtins.input", return_value="Chip"), \
             patch.object(self.app.sample_view, "show_search_result") as mock_show:
            self.app._handle_sample()
        mock_show.assert_called_once()

    # ── _handle_order_reserve ────────────────────────────────
    def test_handle_order_reserve_creates_order(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        with patch.object(self.app.sample_view, "show_list"), \
             patch.object(self.app.order_view, "input_order", return_value={
                 "sample_id": "S001", "customer": "ACME", "quantity": 50,
             }), \
             patch.object(self.app.order_view, "show_order_result"):
            self.app._handle_order_reserve()
        assert len(self.store.orders) == 1

    # ── _handle_order_approve ────────────────────────────────
    def test_handle_order_approve_prints_message_when_no_reserved(self, capsys):
        self.app._handle_order_approve()
        assert "없습니다" in capsys.readouterr().out

    def test_handle_order_approve_returns_on_zero_choice(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        self.app.order_ctrl.reserve("S001", "ACME", 50)
        with patch.object(self.app.order_view, "show_reserved_list"), \
             patch.object(self.app.order_view, "get_order_choice", return_value="0"):
            self.app._handle_order_approve()

    def test_handle_order_approve_approves_selected_order(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        order = self.app.order_ctrl.reserve("S001", "ACME", 50)
        with patch.object(self.app.order_view, "show_reserved_list"), \
             patch.object(self.app.order_view, "get_order_choice", return_value="1"), \
             patch("builtins.input", return_value="y"), \
             patch.object(self.app.order_view, "show_order_result"):
            self.app._handle_order_approve()
        assert self.store.orders[order.order_no].status == OrderStatus.CONFIRMED

    def test_handle_order_approve_rejects_selected_order(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        order = self.app.order_ctrl.reserve("S001", "ACME", 50)
        with patch.object(self.app.order_view, "show_reserved_list"), \
             patch.object(self.app.order_view, "get_order_choice", return_value="1"), \
             patch("builtins.input", return_value="n"), \
             patch.object(self.app.order_view, "show_order_result"):
            self.app._handle_order_approve()
        assert self.store.orders[order.order_no].status == OrderStatus.REJECTED

    # ── _handle_monitoring ───────────────────────────────────
    def test_handle_monitoring_exits_on_zero(self):
        with patch.object(self.app.monitoring_view, "show_submenu", return_value="0"):
            self.app._handle_monitoring()

    def test_handle_monitoring_shows_order_stats(self):
        with patch.object(self.app.monitoring_view, "show_submenu", side_effect=["1", "0"]), \
             patch.object(self.app.monitoring_view, "show_order_stats") as mock_show:
            self.app._handle_monitoring()
        mock_show.assert_called_once()

    def test_handle_monitoring_shows_inventory(self):
        with patch.object(self.app.monitoring_view, "show_submenu", side_effect=["2", "0"]), \
             patch.object(self.app.monitoring_view, "show_inventory") as mock_show:
            self.app._handle_monitoring()
        mock_show.assert_called_once()

    # ── _handle_production ───────────────────────────────────
    def test_handle_production_shows_when_no_current_job(self):
        with patch.object(self.app.production_view, "show_current") as mock_cur, \
             patch.object(self.app.production_view, "show_queue") as mock_queue:
            self.app._handle_production()
        mock_cur.assert_called_once_with(None)
        mock_queue.assert_called_once_with([])

    def test_handle_production_completes_job_on_y(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 5
        order = self.app.order_ctrl.reserve("S001", "ACME", 50)
        self.app.order_ctrl.approve(order.order_no)
        with patch.object(self.app.production_view, "show_current"), \
             patch.object(self.app.production_view, "show_queue"), \
             patch("builtins.input", return_value="y"), \
             patch("builtins.print"):
            self.app._handle_production()
        assert self.store.orders[order.order_no].status == OrderStatus.CONFIRMED

    def test_handle_production_skips_completion_on_n(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 5
        order = self.app.order_ctrl.reserve("S001", "ACME", 50)
        self.app.order_ctrl.approve(order.order_no)
        with patch.object(self.app.production_view, "show_current"), \
             patch.object(self.app.production_view, "show_queue"), \
             patch("builtins.input", return_value="n"):
            self.app._handle_production()
        assert self.store.orders[order.order_no].status == OrderStatus.PRODUCING

    # ── _handle_release ──────────────────────────────────────
    def test_handle_release_prints_message_when_no_confirmed(self, capsys):
        self.app._handle_release()
        assert "없습니다" in capsys.readouterr().out

    def test_handle_release_returns_on_zero_choice(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        order = self.app.order_ctrl.reserve("S001", "ACME", 50)
        self.app.order_ctrl.approve(order.order_no)
        with patch.object(self.app.order_view, "show_confirmed_list"), \
             patch.object(self.app.order_view, "get_order_choice", return_value="0"):
            self.app._handle_release()
        assert self.store.orders[order.order_no].status == OrderStatus.CONFIRMED

    def test_handle_release_releases_selected_order(self):
        self.app.sample_ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.store.samples["S001"].stock = 100
        order = self.app.order_ctrl.reserve("S001", "ACME", 50)
        self.app.order_ctrl.approve(order.order_no)
        with patch.object(self.app.order_view, "show_confirmed_list"), \
             patch.object(self.app.order_view, "get_order_choice", return_value="1"), \
             patch.object(self.app.order_view, "show_order_result"):
            self.app._handle_release()
        assert self.store.orders[order.order_no].status == OrderStatus.RELEASED
