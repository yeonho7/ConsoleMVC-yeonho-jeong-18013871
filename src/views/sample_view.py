from src.models.sample import Sample


class SampleView:
    def show_list(self, samples: list[Sample]):
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        print(f"{'ID':<10} {'이름':<20} {'생산시간':>8} {'수율':>6} {'재고':>6}")
        print("-" * 55)
        for s in samples:
            print(f"{s.sample_id:<10} {s.name:<20} {s.avg_production_time:>7.1f}분 {s.yield_rate:>5.0%} {s.stock:>5}ea")

    def show_search_result(self, samples: list[Sample]):
        if not samples:
            print("검색 결과가 없습니다.")
            return
        self.show_list(samples)

    def input_sample(self) -> dict:
        sample_id = input("시료 ID > ").strip()
        name = input("시료 이름 > ").strip()
        avg_production_time = float(input("평균 생산시간 (분/ea) > ").strip())
        yield_rate = float(input("수율 (0.0~1.0) > ").strip())
        return {
            "sample_id": sample_id,
            "name": name,
            "avg_production_time": avg_production_time,
            "yield_rate": yield_rate,
        }

    def input_search_keyword(self) -> str:
        return input("검색어 > ").strip()

    def show_submenu(self) -> str:
        print("[1] 시료 등록  [2] 목록 조회  [3] 이름 검색  [0] 돌아가기")
        return input("선택 > ").strip()
