from src.controllers.sample_controller import SampleController
from src.controllers.order_controller import OrderController
from src.controllers.production_controller import ProductionController
from src.controllers.monitoring_controller import MonitoringController
from src.views.main_view import MainView
from src.views.sample_view import SampleView
from src.views.order_view import OrderView
from src.views.production_view import ProductionView
from src.views.monitoring_view import MonitoringView


class App:
    def __init__(self, store):
        self.store = store
        self.sample_ctrl = SampleController(store)
        self.order_ctrl = OrderController(store)
        self.production_ctrl = ProductionController(store)
        self.monitoring_ctrl = MonitoringController(store)
        self.main_view = MainView()
        self.sample_view = SampleView()
        self.order_view = OrderView()
        self.production_view = ProductionView()
        self.monitoring_view = MonitoringView()

    def run(self):
        while True:
            summary = self._get_summary()
            self.main_view.show_header(summary)
            self.main_view.show_menu()
            choice = self.main_view.get_choice()
            if choice == "0":
                break
            elif choice == "1":
                self._handle_sample()
            elif choice == "2":
                self._handle_order_reserve()
            elif choice == "3":
                self._handle_order_approve()
            elif choice == "4":
                self._handle_monitoring()
            elif choice == "5":
                self._handle_production()
            elif choice == "6":
                self._handle_release()

    def _get_summary(self) -> dict:
        samples = self.sample_ctrl.list_all()
        return {
            "sample_count": len(samples),
            "total_stock": sum(s.stock for s in samples),
            "total_orders": len(self.store.orders),
            "queue_count": len(self.production_ctrl.get_queue()),
        }

    def _handle_sample(self):
        while True:
            choice = self.sample_view.show_submenu()
            if choice == "0":
                break
            elif choice == "1":
                self.sample_view.show_list(self.sample_ctrl.list_all())
            elif choice == "2":
                data = self.sample_view.input_sample()
                sample = self.sample_ctrl.register(
                    data["sample_id"], data["name"],
                    data["avg_production_time"], data["yield_rate"],
                )
                print(f"시료 [{sample.name}] 등록 완료")
            elif choice == "3":
                keyword = input("검색어: ").strip()
                self.sample_view.show_search_result(self.sample_ctrl.search(keyword))

    def _handle_order_reserve(self):
        self.sample_view.show_list(self.sample_ctrl.list_all())
        data = self.order_view.input_order()
        order = self.order_ctrl.reserve(data["sample_id"], data["customer"], data["quantity"])
        self.order_view.show_order_result(order)

    def _handle_order_approve(self):
        orders = self.order_ctrl.list_reserved()
        if not orders:
            print("승인 대기 중인 주문이 없습니다.")
            return
        self.order_view.show_reserved_list(orders)
        choice = self.order_view.get_order_choice(orders)
        if choice == "0":
            return
        idx = int(choice) - 1
        if 0 <= idx < len(orders):
            order = orders[idx]
            action = input("승인(y) / 거절(n): ").strip().lower()
            if action == "y":
                updated = self.order_ctrl.approve(order.order_no)
            else:
                updated = self.order_ctrl.reject(order.order_no)
            self.order_view.show_order_result(updated)

    def _handle_monitoring(self):
        while True:
            choice = self.monitoring_view.show_submenu()
            if choice == "0":
                break
            elif choice == "1":
                self.monitoring_view.show_order_stats(self.monitoring_ctrl.get_order_stats())
            elif choice == "2":
                self.monitoring_view.show_inventory(self.monitoring_ctrl.get_inventory_status())

    def _handle_production(self):
        job = self.production_ctrl.get_current()
        queue = self.production_ctrl.get_queue()
        self.production_view.show_current(job)
        self.production_view.show_queue(queue)
        if job:
            action = input("현재 작업 완료 처리? (y/n): ").strip().lower()
            if action == "y":
                order = self.production_ctrl.complete_current()
                if order:
                    print(f"주문 [{order.order_no}] 생산 완료 — 확정 처리됨")

    def _handle_release(self):
        orders = self.order_ctrl.list_confirmed()
        if not orders:
            print("출고 가능한 주문이 없습니다.")
            return
        self.order_view.show_confirmed_list(orders)
        choice = self.order_view.get_order_choice(orders)
        if choice == "0":
            return
        idx = int(choice) - 1
        if 0 <= idx < len(orders):
            order = orders[idx]
            updated = self.order_ctrl.release(order.order_no)
            self.order_view.show_order_result(updated)
