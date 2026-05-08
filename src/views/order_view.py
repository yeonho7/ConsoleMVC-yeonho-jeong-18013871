from src.models.order import Order


class OrderView:
    def show_reserved_list(self, orders: list[Order]):
        if not orders:
            print("승인 대기 주문이 없습니다.")
            return
        print(f"{'번호':<5} {'주문번호':<24} {'시료ID':<10} {'고객':<15} {'수량'}")
        print("-" * 65)
        for i, o in enumerate(orders, 1):
            print(f"{i:<5} {o.order_no:<24} {o.sample_id:<10} {o.customer:<15} {o.quantity}")

    def show_confirmed_list(self, orders: list[Order]):
        if not orders:
            print("출고 가능한 주문이 없습니다.")
            return
        print(f"{'번호':<5} {'주문번호':<24} {'시료ID':<10} {'고객':<15} {'수량'}")
        print("-" * 65)
        for i, o in enumerate(orders, 1):
            print(f"{i:<5} {o.order_no:<24} {o.sample_id:<10} {o.customer:<15} {o.quantity}")

    def input_order(self) -> dict:
        sample_id = input("시료 ID: ").strip()
        customer = input("고객명: ").strip()
        quantity = int(input("주문 수량: ").strip())
        return {"sample_id": sample_id, "customer": customer, "quantity": quantity}

    def show_order_result(self, order: Order):
        print(f"\n주문번호: {order.order_no} | 상태: {order.status.value} | "
              f"시료: {order.sample_id} | 고객: {order.customer} | 수량: {order.quantity}")

    def get_order_choice(self, orders: list[Order]) -> str:
        return input("번호 선택 (0=뒤로): ").strip()
