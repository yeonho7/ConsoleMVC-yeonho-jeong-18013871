"""App 라우터 통합 테스트 — 메뉴 흐름을 end-to-end로 검증."""
import pytest
from unittest.mock import patch
from src.store import InMemoryStore
from src.app import App
from src.models.order import OrderStatus


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def app(store):
    return App(store)


class TestAppRun:
    def test_exits_on_zero_input(self, app):
        with patch("builtins.input", return_value="0"):
            app.run()  # 무한루프 없이 종료되어야 함

    def test_unknown_menu_choice_does_not_crash(self, app):
        with patch("builtins.input", side_effect=["9", "0"]):
            app.run()


class TestAppSampleFlow:
    def test_register_sample_via_menu_1(self, app, store):
        inputs = iter(["1", "1", "S-001", "GaAs Wafer", "30.0", "0.9", "0", "0"])
        with patch("builtins.input", side_effect=inputs):
            app.run()
        assert "S-001" in store.samples

    def test_list_samples_via_menu(self, app, store, capsys):
        store.samples["S-001"] = __import__("src.models.sample", fromlist=["Sample"]).Sample(
            "S-001", "GaAs Wafer", 30.0, 0.9, stock=10
        )
        inputs = iter(["1", "2", "0", "0"])
        with patch("builtins.input", side_effect=inputs):
            app.run()
        out = capsys.readouterr().out
        assert "S-001" in out


class TestAppOrderFlow:
    def test_reserve_order_via_menu_2(self, app, store):
        store.samples["S-001"] = __import__("src.models.sample", fromlist=["Sample"]).Sample(
            "S-001", "GaAs Wafer", 30.0, 0.9, stock=10
        )
        inputs = iter(["2", "S-001", "Lab A", "5", "0"])
        with patch("builtins.input", side_effect=inputs):
            app.run()
        assert len(store.orders) == 1

    def test_approve_order_sufficient_stock(self, app, store):
        from src.models.sample import Sample
        from src.models.order import Order
        store.samples["S-001"] = Sample("S-001", "GaAs Wafer", 30.0, 0.9, stock=20)
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=5)
        store.orders["ORD-20260508-0001"] = order

        # 메뉴 3 → 주문 목록에서 1번 선택 → 승인(1)
        inputs = iter(["3", "1", "1", "0"])
        with patch("builtins.input", side_effect=inputs):
            app.run()
        assert store.orders["ORD-20260508-0001"].status == OrderStatus.CONFIRMED

    def test_reject_order_via_menu_3(self, app, store):
        from src.models.sample import Sample
        from src.models.order import Order
        store.samples["S-001"] = Sample("S-001", "GaAs Wafer", 30.0, 0.9, stock=20)
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=5)
        store.orders["ORD-20260508-0001"] = order

        # 메뉴 3 → 1번 선택 → 거절(2)
        inputs = iter(["3", "1", "2", "0"])
        with patch("builtins.input", side_effect=inputs):
            app.run()
        assert store.orders["ORD-20260508-0001"].status == OrderStatus.REJECTED


class TestAppReleaseFlow:
    def test_release_confirmed_order_via_menu_6(self, app, store):
        from src.models.sample import Sample
        from src.models.order import Order
        store.samples["S-001"] = Sample("S-001", "GaAs Wafer", 30.0, 0.9, stock=20)
        order = Order(order_no="ORD-20260508-0001", sample_id="S-001", customer="Lab A", quantity=5,
                      status=OrderStatus.CONFIRMED)
        store.orders["ORD-20260508-0001"] = order

        inputs = iter(["6", "1", "0"])
        with patch("builtins.input", side_effect=inputs):
            app.run()
        assert store.orders["ORD-20260508-0001"].status == OrderStatus.RELEASED
