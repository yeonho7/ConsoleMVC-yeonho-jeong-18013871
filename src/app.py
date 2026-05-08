from src.store import InMemoryStore
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
    def __init__(self, store: InMemoryStore):
        self._store = store
        self._sample_ctrl = SampleController(store)
        self._production_ctrl = ProductionController(store)
        self._order_ctrl = OrderController(store, self._production_ctrl)
        self._monitoring_ctrl = MonitoringController(store)

        self._main_view = MainView()
        self._sample_view = SampleView()
        self._order_view = OrderView()
        self._production_view = ProductionView()
        self._monitoring_view = MonitoringView()

    def run(self):
        while True:
            self._main_view.show_header(self._get_summary())
            self._main_view.show_menu()
            choice = self._main_view.get_choice()

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
        total_stock = sum(s.stock for s in self._store.samples.values())
        queue_count = len(self._store.production_queue)
        return {
            "sample_count": len(self._store.samples),
            "total_stock": total_stock,
            "order_count": len(self._store.orders),
            "queue_count": queue_count,
        }

    def _handle_sample(self):
        while True:
            choice = self._sample_view.show_submenu()
            if choice == "0":
                break
            elif choice == "1":
                data = self._sample_view.input_sample()
                self._sample_ctrl.register(
                    data["sample_id"], data["name"],
                    data["avg_production_time"], data["yield_rate"]
                )
            elif choice == "2":
                self._sample_view.show_list(self._sample_ctrl.list_all())
            elif choice == "3":
                keyword = self._sample_view.input_search_keyword()
                self._sample_view.show_search_result(self._sample_ctrl.search(keyword))

    def _handle_order_reserve(self):
        data = self._order_view.input_order()
        order = self._order_ctrl.reserve(data["sample_id"], data["customer"], data["quantity"])
        self._order_view.show_order_result(order)

    def _handle_order_approve(self):
        orders = self._order_ctrl.list_reserved()
        self._order_view.show_reserved_list(orders)
        if not orders:
            return
        choice = self._order_view.get_order_choice(orders)
        try:
            idx = int(choice) - 1
            order = orders[idx]
        except (ValueError, IndexError):
            return
        action = self._order_view.get_approve_or_reject()
        if action == "1":
            self._order_ctrl.approve(order.order_no)
        elif action == "2":
            self._order_ctrl.reject(order.order_no)

    def _handle_monitoring(self):
        while True:
            choice = self._monitoring_view.show_submenu()
            if choice == "0":
                break
            elif choice == "1":
                stats = self._monitoring_ctrl.get_order_stats()
                self._monitoring_view.show_order_stats(stats)
            elif choice == "2":
                inventory = self._monitoring_ctrl.get_inventory_status()
                self._monitoring_view.show_inventory(inventory)

    def _handle_production(self):
        self._production_view.show_current(self._production_ctrl.get_current())
        self._production_view.show_queue(self._production_ctrl.get_queue())
        if self._store.current_job:
            if self._production_view.ask_complete_current():
                self._production_ctrl.complete_current()

    def _handle_release(self):
        orders = self._order_ctrl.list_confirmed()
        self._order_view.show_confirmed_list(orders)
        if not orders:
            return
        choice = self._order_view.get_order_choice(orders)
        try:
            idx = int(choice) - 1
            order = orders[idx]
        except (ValueError, IndexError):
            return
        self._order_ctrl.release(order.order_no)
        self._order_view.show_release_result(order)
