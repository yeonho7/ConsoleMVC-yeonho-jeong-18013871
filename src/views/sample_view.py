from src.models.sample import Sample


class SampleView:
    def show_list(self, samples: list[Sample]):
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        print(f"{'ID':<10} {'이름':<20} {'생산시간(분/ea)':<16} {'수율':<8} {'재고'}")
        print("-" * 60)
        for s in samples:
            print(f"{s.sample_id:<10} {s.name:<20} {s.avg_production_time:<16} {s.yield_rate:<8} {s.stock}")

    def show_search_result(self, samples: list[Sample]):
        if not samples:
            print("검색 결과가 없습니다.")
            return
        self.show_list(samples)

    def input_sample(self) -> dict:
        sample_id = input("시료 ID: ").strip()
        name = input("시료명: ").strip()
        avg_production_time = float(input("평균 생산시간(분/ea): ").strip())
        yield_rate = float(input("수율(0.0~1.0): ").strip())
        return {
            "sample_id": sample_id,
            "name": name,
            "avg_production_time": avg_production_time,
            "yield_rate": yield_rate,
        }

    def show_submenu(self) -> str:
        print("\n[시료 관리]")
        print("[1] 목록 조회  [2] 시료 등록  [3] 시료 검색  [0] 뒤로")
        return input("선택 > ").strip()
