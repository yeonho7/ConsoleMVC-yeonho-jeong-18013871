from src.models.order import Order


class OrderView:
    def show_reserved_list(self, orders: list[Order]):
        if not orders:
            print("접수된 주문이 없습니다.")
            return
        print(f"{'#':<4} {'주문번호':<22} {'시료ID':<10} {'고객명':<15} {'수량':>5}")
        print("-" * 60)
        for i, o in enumerate(orders, 1):
            print(f"{i:<4} {o.order_no:<22} {o.sample_id:<10} {o.customer:<15} {o.quantity:>4}ea")

    def show_confirmed_list(self, orders: list[Order]):
        if not orders:
            print("출고 대기 주문이 없습니다.")
            return
        print(f"{'#':<4} {'주문번호':<22} {'시료ID':<10} {'고객명':<15} {'수량':>5}")
        print("-" * 60)
        for i, o in enumerate(orders, 1):
            print(f"{i:<4} {o.order_no:<22} {o.sample_id:<10} {o.customer:<15} {o.quantity:>4}ea")

    def input_order(self) -> dict:
        sample_id = input("시료 ID > ").strip()
        customer = input("고객명 > ").strip()
        quantity = int(input("주문 수량 > ").strip())
        return {"sample_id": sample_id, "customer": customer, "quantity": quantity}

    def show_order_result(self, order: Order):
        print(f"주문 접수 완료: {order.order_no}  [{order.status.value}]")

    def get_order_choice(self, orders: list[Order]) -> str:
        return input("선택할 번호 > ").strip()
