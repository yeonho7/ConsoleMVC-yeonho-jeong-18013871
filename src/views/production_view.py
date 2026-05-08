from src.models.production_job import ProductionJob


class ProductionView:
    def show_current(self, job: ProductionJob | None):
        print("[ 현재 생산 중 ]")
        if job is None:
            print("  생산 중인 작업 없음")
            return
        print(f"  주문번호: {job.order_no}  시료: {job.sample_id}")
        print(f"  부족분: {job.shortage}ea  실 생산량: {job.actual_qty}ea  총 시간: {job.total_time:.1f}분")

    def show_queue(self, jobs: list[ProductionJob]):
        print("[ 생산 대기 큐 ]")
        if not jobs:
            print("  대기 중인 작업 없음")
            return
        for i, job in enumerate(jobs, 1):
            print(f"  {i}. {job.order_no}  시료: {job.sample_id}  실 생산량: {job.actual_qty}ea")
