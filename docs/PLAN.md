# PLAN — ConsoleMVC PoC 구현 계획

> 이 계획은 `docs/PRD.md`를 기반으로 MVC 스켈레톤 코드를 단계별로 구현한다.  
> 각 단계는 독립적으로 검증 가능하도록 구성한다.

## 참조 레포

| 레포 | 이 계획에서의 역할 |
|------|------------------|
| [DataPersistence](https://github.com/yeonho7/DataPersistence-yeonho-jeong-18013871) | Step 2 Model 설계의 참조 아키텍처. `OrderStatus`를 Enum으로 유지하는 이유: 타입 안전성. `order_no` 필드명은 DataPersistence의 `order_id`와 다름. |
| [DummyDataGenerator](https://github.com/yeonho7/DummyDataGenerator-yeonho-jeong-18013871) | 통합 검증 시나리오에 사용할 더미 데이터 생성 도구 (12종 시료 / 36건 주문 / 생산작업 포함) |
| [DataMonitor](https://github.com/yeonho7/DataMonitor-yeonho.jeong-18013871) | Step 4 MonitoringController 및 Step 5 MonitoringView의 참조 구현 |

---

---

## 구현 순서

```
Step 1: 프로젝트 골격 세팅
Step 2: Models 구현
Step 3: InMemoryStore 구현
Step 4: Controllers 구현
Step 5: Views 구현
Step 6: App 라우터 구현
Step 7: 진입점 및 동작 검증
```

---

## Step 1 — 프로젝트 골격 세팅

**목표**: 디렉터리 구조 생성 및 패키지 초기화

```
ConsoleMVC/
├── main.py
└── src/
    ├── app.py
    ├── store.py
    ├── models/__init__.py
    ├── controllers/__init__.py
    └── views/__init__.py
```

**작업 목록**:
- [ ] `src/` 하위 패키지 디렉터리 생성
- [ ] 각 패키지 `__init__.py` 파일 생성 (빈 파일)
- [ ] `main.py` 빈 진입점 생성

**검증**: `python main.py` 실행 시 오류 없이 종료

---

## Step 2 — Models 구현

**목표**: 데이터 구조 정의. 비즈니스 로직 없음.

> **DataPersistence 참조**: DataPersistence의 model(Sample·Order·ProductionJob)과 동일한 도메인. 단, 여기서는 `Order.status`를 `str` 대신 `OrderStatus` Enum으로, 주문 식별자를 `order_id` 대신 `order_no`로 정의한다.

### `src/models/order.py`
```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class OrderStatus(Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASED = "RELEASED"

@dataclass
class Order:
    order_no: str
    sample_id: str
    customer: str
    quantity: int
    status: OrderStatus = OrderStatus.RESERVED
    created_at: datetime = field(default_factory=datetime.now)
    released_at: datetime | None = None
```

### `src/models/sample.py`
```python
@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float   # 분/ea
    yield_rate: float            # 0.0 ~ 1.0
    stock: int = 0
```

### `src/models/production_job.py`
```python
@dataclass
class ProductionJob:
    order_no: str
    sample_id: str
    shortage: int        # 부족분 = 주문수량 - 재고
    actual_qty: int      # ceil(shortage / (yield_rate * 0.9))
    total_time: float    # avg_production_time * actual_qty (분)
```

**검증**: `from src.models.order import Order, OrderStatus` import 성공

---

## Step 3 — InMemoryStore 구현

**목표**: 모든 컨트롤러가 공유하는 단일 데이터 저장소

### `src/store.py`
```python
from collections import deque
from src.models.sample import Sample
from src.models.order import Order
from src.models.production_job import ProductionJob

class InMemoryStore:
    def __init__(self):
        self.samples: dict[str, Sample] = {}
        self.orders: dict[str, Order] = {}
        self.production_queue: deque[ProductionJob] = deque()
        self.current_job: ProductionJob | None = None
        self._order_counter: int = 0

    def next_order_no(self) -> str:
        self._order_counter += 1
        from datetime import date
        today = date.today().strftime("%Y%m%d")
        return f"ORD-{today}-{self._order_counter:04d}"
```

**검증**: `store = InMemoryStore()` 인스턴스 생성 성공

---

## Step 4 — Controllers 구현

**규칙**: `print()` / `input()` 호출 금지. 순수 로직만.

### `src/controllers/sample_controller.py`
```python
class SampleController:
    def __init__(self, store): ...

    def register(self, sample_id, name, avg_time, yield_rate) -> Sample:
        # Sample 생성 후 store.samples에 저장
        ...

    def list_all(self) -> list[Sample]:
        # store.samples.values() 반환
        ...

    def search(self, keyword) -> list[Sample]:
        # name에 keyword 포함된 시료 반환
        ...
```

### `src/controllers/order_controller.py`
```python
class OrderController:
    def __init__(self, store): ...

    def reserve(self, sample_id, customer, quantity) -> Order:
        # Order 생성, store.orders 저장, RESERVED
        ...

    def approve(self, order_no) -> Order:
        # 재고 확인:
        #   재고 >= qty → CONFIRMED
        #   재고 < qty  → ProductionJob 생성, enqueue, PRODUCING
        ...

    def reject(self, order_no) -> Order:
        # REJECTED 전환
        ...

    def release(self, order_no) -> Order:
        # CONFIRMED → RELEASED, released_at 기록
        ...

    def list_reserved(self) -> list[Order]: ...
    def list_confirmed(self) -> list[Order]: ...
```

**approve 내부 생산량 계산**:
```python
import math
shortage = quantity - sample.stock
actual_qty = math.ceil(shortage / (sample.yield_rate * 0.9))
total_time = sample.avg_production_time * actual_qty
```

### `src/controllers/production_controller.py`
```python
class ProductionController:
    def __init__(self, store): ...

    def enqueue(self, job: ProductionJob) -> ProductionJob:
        # store.production_queue.append(job)
        ...

    def complete_current(self) -> Order | None:
        # current_job 완료 → 해당 Order CONFIRMED 전환
        # 큐에서 다음 job 꺼내 current_job 설정
        ...

    def get_current(self) -> ProductionJob | None: ...
    def get_queue(self) -> list[ProductionJob]: ...
```

### `src/controllers/monitoring_controller.py`
```python
class MonitoringController:
    def __init__(self, store): ...

    def get_order_stats(self) -> dict:
        # 상태별 주문 건수 집계 (REJECTED 제외)
        ...

    def get_inventory_status(self) -> list[dict]:
        # 시료별 재고 + 상태(여유/부족/고갈)
        # 고갈: stock == 0
        # 부족: 해당 시료 RESERVED+PRODUCING 주문 합계 > stock
        # 여유: 그 외
        ...
```

**검증**: 각 컨트롤러 import 성공, 기본 메서드 호출 가능

---

## Step 5 — Views 구현

**규칙**: 비즈니스 로직 없음. 데이터를 받아 출력하거나 입력을 수집해 반환.

### `src/views/main_view.py`
```python
class MainView:
    def show_header(self, summary: dict): ...
    # summary = {시료수, 총재고, 전체주문수, 생산대기수}

    def show_menu(self): ...
    # [1] 시료 관리  [2] 시료 주문 ...

    def get_choice(self) -> str:
        return input("선택 > ").strip()
```

### `src/views/sample_view.py`
```python
class SampleView:
    def show_list(self, samples: list[Sample]): ...
    def show_search_result(self, samples: list[Sample]): ...
    def input_sample(self) -> dict:
        # 시료 ID, 이름, 평균 생산시간, 수율 입력받아 dict 반환
        ...
    def show_submenu(self) -> str: ...
```

### `src/views/order_view.py`
```python
class OrderView:
    def show_reserved_list(self, orders: list[Order]): ...
    def show_confirmed_list(self, orders: list[Order]): ...
    def input_order(self) -> dict:
        # 시료 ID, 고객명, 주문 수량 입력받아 dict 반환
        ...
    def show_order_result(self, order: Order): ...
    def get_order_choice(self, orders: list[Order]) -> str: ...
```

### `src/views/production_view.py`
```python
class ProductionView:
    def show_current(self, job: ProductionJob | None): ...
    def show_queue(self, jobs: list[ProductionJob]): ...
```

### `src/views/monitoring_view.py`
```python
class MonitoringView:
    def show_order_stats(self, stats: dict): ...
    def show_inventory(self, inventory: list[dict]): ...
    def show_submenu(self) -> str: ...
```

**검증**: 각 View import 성공, 더미 데이터로 출력 확인

---

## Step 6 — App 라우터 구현

**목표**: 메인 루프 및 메뉴 라우팅

### `src/app.py`
```python
class App:
    def __init__(self, store):
        # 컨트롤러 초기화
        self.sample_ctrl = SampleController(store)
        self.order_ctrl = OrderController(store)
        self.production_ctrl = ProductionController(store)
        self.monitoring_ctrl = MonitoringController(store)
        # 뷰 초기화
        self.main_view = MainView()
        self.sample_view = SampleView()
        self.order_view = OrderView()
        self.production_view = ProductionView()
        self.monitoring_view = MonitoringView()

    def run(self):
        while True:
            summary = self._get_summary()
            self.main_view.show_header(summary)
            self.main_view.show_menu()
            choice = self.main_view.get_choice()

            if choice == "0":
                break
            elif choice == "1":
                self._handle_sample()
            elif choice == "2":
                self._handle_order_reserve()
            elif choice == "3":
                self._handle_order_approve()
            elif choice == "4":
                self._handle_monitoring()
            elif choice == "5":
                self._handle_production()
            elif choice == "6":
                self._handle_release()

    def _handle_sample(self): ...
    def _handle_order_reserve(self): ...
    def _handle_order_approve(self): ...
    def _handle_monitoring(self): ...
    def _handle_production(self): ...
    def _handle_release(self): ...
    def _get_summary(self) -> dict: ...
```

**검증**: `App(store).run()` 실행 시 메인 메뉴 출력, 0 입력 시 종료

---

## Step 7 — 진입점 및 통합 검증

### `main.py`
```python
from src.store import InMemoryStore
from src.app import App

if __name__ == "__main__":
    store = InMemoryStore()
    app = App(store)
    app.run()
```

**통합 검증 시나리오**:

| 시나리오 | 검증 항목 |
|----------|-----------|
| 시료 등록 후 목록 조회 | Sample이 store에 저장되어 목록에 표시 |
| 주문 접수 | RESERVED 상태로 생성, 주문번호 발급 |
| 재고 충분 시 승인 | 즉시 CONFIRMED 전환 |
| 재고 부족 시 승인 | PRODUCING 전환, 생산 큐 등록 |
| 주문 거절 | REJECTED 전환, 모니터링에서 제외 |
| 출고 처리 | CONFIRMED → RELEASED 전환 |
| 모니터링 | 상태별 건수 및 재고 상태 정확히 표시 |
| 생산라인 조회 | 현재 작업 및 FIFO 대기 큐 표시 |

---

## 완료 기준

- [ ] `python main.py` 실행 후 메인 메뉴 진입
- [ ] 6개 메뉴 전부 접근 가능 (오류 없음)
- [ ] Controller가 `print()` / `input()` 직접 호출하지 않음
- [ ] View가 비즈니스 로직을 포함하지 않음
- [ ] Model이 순수 데이터 구조로만 구성됨
- [ ] 통합 검증 시나리오 7개 모두 통과
