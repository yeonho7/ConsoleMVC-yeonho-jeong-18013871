from src.models.production_job import ProductionJob


class ProductionView:
    def show_current(self, job: ProductionJob | None):
        print("\n[현재 생산 작업]")
        if job is None:
            print("  진행 중인 생산 작업이 없습니다.")
        else:
            print(f"  주문번호: {job.order_no} | 시료: {job.sample_id} | "
                  f"부족량: {job.shortage}ea | 생산량: {job.actual_qty}ea | "
                  f"예상시간: {job.total_time:.0f}분")

    def show_queue(self, jobs: list[ProductionJob]):
        print("\n[생산 대기 큐]")
        if not jobs:
            print("  대기 중인 작업이 없습니다.")
        else:
            for i, job in enumerate(jobs, 1):
                print(f"  {i}. {job.order_no} | 시료: {job.sample_id} | 생산량: {job.actual_qty}ea")
