# ConsoleMVC — 반도체 시료 생산주문관리 MVC 스켈레톤 PoC

Python 콘솔 기반으로 **Model / Controller / View 계층 분리**를 증명하는 PoC입니다.  
가상의 반도체 회사 S-Semi의 시료 생산주문관리 시스템을 도메인으로 사용합니다.

> **목적**: MVC 구조와 주문 워크플로우가 실제로 동작하는지 검증.  
> 데이터 영속성·더미 데이터 생성·모니터링은 별도 PoC([에코시스템](#poc-에코시스템))에서 담당합니다.

---

## 빠른 시작

```bash
# 1. 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 2. 앱 실행
python main.py
```

외부 의존성 없음. Python 3 표준 라이브러리만 사용합니다 (`math`, `datetime`, `collections.deque`, `dataclasses`, `enum`).

---

## 프로젝트 구조

```
ConsoleMVC/
├── main.py                          # 진입점 — InMemoryStore + App 생성
├── src/
│   ├── app.py                       # 메인 루프 + 메뉴 라우터
│   ├── store.py                     # InMemoryStore — 공유 데이터 저장소
│   ├── models/
│   │   ├── sample.py                # Sample 데이터 클래스
│   │   ├── order.py                 # Order + OrderStatus enum
│   │   └── production_job.py        # ProductionJob 데이터 클래스
│   ├── controllers/
│   │   ├── sample_controller.py     # 시료 등록·조회·검색
│   │   ├── order_controller.py      # 주문 접수·승인·거절·출고
│   │   ├── production_controller.py # 생산 큐 관리
│   │   └── monitoring_controller.py # 주문 통계·재고 현황
│   └── views/
│       ├── main_view.py             # 메인 메뉴 헤더·입력
│       ├── sample_view.py
│       ├── order_view.py
│       ├── production_view.py
│       └── monitoring_view.py
├── tests/                           # pytest 단위 테스트 (110개, 커버리지 100%)
└── docs/
    ├── PRD.md                       # 상세 요구사항
    └── PLAN.md                      # 단계별 구현 계획
```

---

## 아키텍처

```
main.py
  └── App(store)          ← InMemoryStore 주입
        ├── Controllers   ← 비즈니스 로직, Store 읽기/쓰기
        └── Views         ← input() 수집, print() 출력
```

**데이터 흐름**:  
`View` 입력 수집 → `Controller` 비즈니스 로직 처리 → `Store` 상태 변경 → 결과 반환 → `View` 출력

### 계층별 책임 규칙

| 계층 | 역할 | 금지 |
|------|------|------|
| **Model** | 데이터 구조, 상태 보유 | 비즈니스 로직, 출력 |
| **Controller** | 비즈니스 로직, 상태 전이, Store 접근 | `print()` / `input()` 직접 호출 |
| **View** | `input()` 수집, `print()` 출력 | 비즈니스 로직, Store 직접 접근 |

---

## 도메인 모델

```python
@dataclass
class Sample:
    sample_id: str            # 예: "S-001"
    name: str
    avg_production_time: float  # 분/개
    yield_rate: float           # 0.0 ~ 1.0
    stock: int = 0

@dataclass
class Order:
    order_no: str             # 예: "ORD-20260508-0001"
    sample_id: str
    customer: str
    quantity: int
    status: OrderStatus       # RESERVED | REJECTED | PRODUCING | CONFIRMED | RELEASED
    created_at: datetime
    released_at: datetime | None = None

@dataclass
class ProductionJob:
    order_no: str
    sample_id: str
    shortage: int             # 주문 수량 - 현재 재고
    actual_qty: int           # ceil(부족분 / (수율 × 0.9))
    total_time: float         # 평균 생산시간 × 실 생산량 (분)
```

---

## 주문 상태 흐름

```
RESERVED ──── 거절 ──────────────────► REJECTED
    │
    └── 승인
          ├── 재고 충분 ──────────────► CONFIRMED ──► RELEASED
          └── 재고 부족 ──► PRODUCING ─► CONFIRMED ──► RELEASED
```

---

## 핵심 비즈니스 로직

### 생산량 계산 (`order_controller.py:approve`)

```python
shortage   = quantity - sample.stock
actual_qty = math.ceil(shortage / (sample.yield_rate * 0.9))
total_time = sample.avg_production_time * actual_qty
```

### 재고 상태 판정 (`monitoring_controller.py:get_inventory_status`)

| 상태 | 조건 |
|------|------|
| 고갈 | `stock == 0` |
| 부족 | RESERVED + PRODUCING 주문 합계 > stock |
| 여유 | 그 외 |

### 주문번호 형식

`ORD-YYYYMMDD-XXXX` — `InMemoryStore.next_order_no()`가 발급. 일자별 0001부터 순번 증가.

---

## 메뉴 구성

| 번호 | 메뉴 | 기능 |
|------|------|------|
| 1 | 시료 관리 | 등록 / 목록 조회 / 이름 검색 |
| 2 | 시료 주문 | 주문 접수 → RESERVED |
| 3 | 주문 승인/거절 | RESERVED 목록 확인 후 승인 또는 거절 |
| 4 | 모니터링 | 상태별 주문 건수 / 시료별 재고 현황 |
| 5 | 생산라인 조회 | 현재 작업 + FIFO 대기 큐, 완료 처리 |
| 6 | 출고 처리 | CONFIRMED → RELEASED |
| 0 | 종료 | |

---

## 테스트 실행

```bash
python -m pytest
```

110개 테스트, 커버리지 100%. TDD로 구현되었습니다.

```bash
# 커버리지 리포트 출력
python -m pytest --cov=src --cov-report=term-missing
```

---

## PoC 에코시스템

ConsoleMVC는 반도체 시료 생산주문관리 아키텍처 검증 시리즈의 일부입니다.

| 레포 | 역할 |
|------|------|
| **ConsoleMVC** (이 레포) | MVC 계층 분리 + 전체 주문 워크플로우 — InMemory 저장소 |
| DataPersistence | JSON write-through 영속성 — model + repository 계층 |
| DummyDataGenerator | 더미 데이터 생성 CLI — 12종 시료 / 36건 주문 |
| DataMonitor | 조회 전용 모니터링 콘솔 |

### DataPersistence와의 주요 차이

| 항목 | ConsoleMVC | DataPersistence |
|------|-----------|----------------|
| Order 상태 타입 | `OrderStatus` Enum | `str` |
| 주문 식별자 필드명 | `order_no` | `order_id` |
| 저장소 | `InMemoryStore` | JSON 파일 |
| 영속성 | 없음 (재시작 시 초기화) | JSON write-through |

---

## PoC 범위

이 레포는 **구조 증명**이 목적입니다. 아래는 의도적으로 제외했습니다.

- 데이터 영속성 (DataPersistence PoC 담당)
- 실시간 생산 시뮬레이션
- 입력 유효성 검사 (엣지 케이스)
