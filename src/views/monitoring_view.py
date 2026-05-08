class MonitoringView:
    def show_order_stats(self, stats: dict):
        print("\n[주문 현황]")
        for status, count in stats.items():
            print(f"  {status.value:<12}: {count}건")

    def show_inventory(self, inventory: list[dict]):
        print("\n[재고 현황]")
        if not inventory:
            print("  등록된 시료가 없습니다.")
            return
        print(f"  {'시료ID':<10} {'이름':<20} {'재고':<8} {'상태'}")
        print("  " + "-" * 45)
        for entry in inventory:
            print(f"  {entry['sample_id']:<10} {entry['name']:<20} {entry['stock']:<8} {entry['status']}")

    def show_submenu(self) -> str:
        print("\n[모니터링]")
        print("[1] 주문 현황  [2] 재고 현황  [0] 뒤로")
        return input("선택 > ").strip()
