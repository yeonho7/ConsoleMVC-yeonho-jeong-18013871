class MainView:
    def show_header(self, summary: dict):
        print("=" * 50)
        print("  반도체 시료 생산주문관리 시스템")
        print("=" * 50)
        print(f"  시료: {summary['sample_count']}종 | 총재고: {summary['total_stock']}ea | "
              f"주문: {summary['total_orders']}건 | 생산대기: {summary['queue_count']}건")
        print("-" * 50)

    def show_menu(self):
        print("[1] 시료 관리")
        print("[2] 주문 접수")
        print("[3] 주문 승인/거절")
        print("[4] 모니터링")
        print("[5] 생산라인")
        print("[6] 출고 처리")
        print("[0] 종료")

    def get_choice(self) -> str:
        return input("선택 > ").strip()
