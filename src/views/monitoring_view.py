from src.models.order import OrderStatus


class MonitoringView:
    def show_order_stats(self, stats: dict):
        print("[ 주문 현황 ]")
        labels = {
            OrderStatus.RESERVED: "접수",
            OrderStatus.PRODUCING: "생산중",
            OrderStatus.CONFIRMED: "출고대기",
            OrderStatus.RELEASED: "출고완료",
        }
        for status, label in labels.items():
            count = stats.get(status, 0)
            print(f"  {label}: {count}건")

    def show_inventory(self, inventory: list[dict]):
        print("[ 재고 현황 ]")
        print(f"{'시료ID':<10} {'이름':<20} {'재고':>6} {'상태':>5}")
        print("-" * 45)
        for item in inventory:
            print(f"{item['sample_id']:<10} {item['name']:<20} {item['stock']:>5}ea {item['status']:>4}")

    def show_submenu(self) -> str:
        print("[1] 주문 현황  [2] 재고 현황  [0] 돌아가기")
        return input("선택 > ").strip()
