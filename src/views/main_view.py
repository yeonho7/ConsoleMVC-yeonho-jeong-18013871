class MainView:
    def show_header(self, summary: dict):
        print("=" * 50)
        print("  S-Semi 시료 생산주문관리 시스템")
        print("=" * 50)
        print(f"  등록 시료: {summary.get('sample_count', 0)}종  |  총 재고: {summary.get('total_stock', 0)}ea")
        print(f"  전체 주문: {summary.get('order_count', 0)}건  |  생산 대기: {summary.get('queue_count', 0)}건")
        print("-" * 50)

    def show_menu(self):
        print("[1] 시료 관리")
        print("[2] 시료 주문")
        print("[3] 주문 승인/거절")
        print("[4] 모니터링")
        print("[5] 생산라인 조회")
        print("[6] 출고 처리")
        print("[0] 종료")

    def get_choice(self) -> str:
        return input("선택 > ").strip()
