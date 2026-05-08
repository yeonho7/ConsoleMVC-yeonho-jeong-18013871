# PRD — ConsoleMVC PoC (반도체 시료 생산주문관리 MVC 스켈레톤)

## 1. 개요

**미션**: MVC 스켈레톤 코드 PoC — Model / Controller / View 패키지 구조와 역할 분리 증명  
**언어**: Python 3  
**실행 방식**: 콘솔(터미널) 기반 대화형 애플리케이션  
**데이터 저장**: In-memory (영속성은 별도 DataPersistence PoC 담당)

---
[
## 2. 배경

가상의 반도체 회사 S-Semi는 다양한 반도체 시료(Sample)를 생산하여 연구소, 팹리스 업체, 대학 연구실 등에 납품한다. 주문량 급증으로 엑셀·메모장 기반 관리에 한계가 생겨 콘솔 기반 생산주문관리 시스템을 개발하기로 했다.

이 PoC는 전체 시스템 개발 전, MVC 계층 분리가 실제로 동작하는지 검증하기 위한 스켈레톤 구현이다.

---

## 3. 역할

| 역할 | 설명 |]()
|------|------|
| 고객 | 시료 요청자. 필요한 시료를 이메일로 요청 |
| 주문 담당자 | 요청에 맞게 주문서 작성 및 관리 |
| 생산 담당자 | 개발 시료 등록, 주문 수신 후 승인 또는 거절 |

---

## 4. 주문 상태 흐름

```
주문 접수 (RESERVED)
    │
    ├─ 거절 → REJECTED  (모니터링 제외)
    │
    └─ 승인
          ├─ 재고 충분 → CONFIRMED → RELEASED
          └─ 재고 부족 → PRODUCING → (생산 완료) → CONFIRMED → RELEASED
```

| 상태 | 의미 |
|------|------|
| RESERVED | 주문 접수 |
| REJECTED | 주문 거절 |
| PRODUCING | 승인 완료 + 재고 부족으로 생산 중 |
| CONFIRMED | 승인 완료 + 출고 대기 중 |
| RELEASED | 출고 완료 |

---

## 5. 기능 명세

### 5.1 메인 메뉴

시스템 현황(등록 시료 수, 총 재고, 전체 주문 수, 생산라인 대기)을 헤더에 표시하고 메뉴를 선택한다.

| 번호 | 메뉴 | 설명 |
|------|------|------|
| 1 | 시료 관리 | 시료 등록 / 목록 조회 / 이름 검색 |
| 2 | 시료 주문 | 고객 주문 접수 (RESERVED) |
| 3 | 주문 승인/거절 | RESERVED 목록 확인 후 승인 또는 거절 |
| 4 | 모니터링 | 상태별 주문 수 및 시료별 재고 현황 |
| 5 | 생산라인 조회 | 현재 생산 중인 시료 및 대기 큐 확인 |
| 6 | 출고 처리 | CONFIRMED 주문 출고 실행 (→ RELEASED) |
| 0 | 종료 | 애플리케이션 종료 |

### 5.2 시료 관리

시료(Sample)는 시스템의 기본 단위. 등록된 시료만 주문 가능.

| 서브 메뉴 | 입력 | 출력 |
|-----------|------|------|
| 시료 등록 | 시료 ID, 이름, 평균 생산시간(min/ea), 수율 | 등록 완료 메시지 |
| 시료 목록 조회 | - | ID / 이름 / 평균 생산시간 / 수율 / 현재 재고 |
| 시료 검색 | 검색 키워드 | 매칭되는 시료 목록 |

> **수율**: 정상적인 시료 / 총 생산 시료 (예: 90/100 = 0.9)

### 5.3 시료 주문

| 입력 항목 | 설명 |
|-----------|------|
| 시료 ID | 등록된 시료만 가능 |
| 고객명 | 자유 문자열 |
| 주문 수량 | 양의 정수 |

- 접수 완료 시 주문번호 발급 (형식: `ORD-YYYYMMDD-XXXX`)
- 초기 상태: `RESERVED`

### 5.4 주문 승인/거절

- `RESERVED` 상태 주문 목록을 표시
- 특정 주문 선택 후 승인 또는 거절

**승인 처리 로직:**
```
재고 확인
  재고 >= 주문 수량  →  상태: CONFIRMED
  재고 < 주문 수량   →  생산라인에 자동 등록, 상태: PRODUCING
```

**거절 처리:** 즉시 `REJECTED` 전환

### 5.5 모니터링

**주문량 확인**: 상태별(RESERVED / CONFIRMED / PRODUCING / RELEASED) 주문 건수 표시. REJECTED 제외.

**재고량 확인**: 시료별 현재 재고 수량 및 재고 상태 표기

| 상태 | 조건 |
|------|------|
| 여유 | 주문 대비 재고 충분 |
| 부족 | 주문 대비 재고 수량 부족 |
| 고갈 | 재고 수량 = 0 |

### 5.6 생산라인 조회

- 생산 라인 1개 (단일 라인), 스케줄링 전략: FIFO
- **실 생산량**: `ceil(부족분 / (수율 * 0.9))`
- **총 생산 시간**: `평균 생산시간 × 실 생산량`
- 생산 완료 시: `PRODUCING → CONFIRMED`

표시 정보:
- 현재 생산 중인 작업 (주문번호, 시료, 주문량, 부족분, 실 생산량, 총 생산시간)
- 대기 중인 작업 목록 (FIFO 순서)

### 5.7 출고 처리

- `CONFIRMED` 상태 주문 목록 표시
- 특정 주문 선택 → `RELEASED` 전환
- 처리일시 기록

---

## 6. MVC 아키텍처 설계

### 6.1 디렉터리 구조

```
ConsoleMVC/
├── main.py                      # 진입점
├── PRD.md
└── src/
    ├── app.py                   # 메인 루프 + 메뉴 라우터
    ├── store.py                 # InMemoryStore (공유 데이터 저장소)
    ├── models/
    │   ├── __init__.py
    │   ├── sample.py            # Sample 데이터 클래스
    │   ├── order.py             # Order 데이터 클래스 + OrderStatus enum
    │   └── production_job.py    # ProductionJob 데이터 클래스
    ├── controllers/
    │   ├── __init__.py
    │   ├── sample_controller.py
    │   ├── order_controller.py
    │   ├── production_controller.py
    │   └── monitoring_controller.py
    └── views/
        ├── __init__.py
        ├── main_view.py
        ├── sample_view.py
        ├── order_view.py
        ├── production_view.py
        └── monitoring_view.py
```

### 6.2 계층별 책임

| 계층 | 책임 | 금지 사항 |
|------|------|-----------|
| Model | 데이터 구조 정의, 상태 보유 | 비즈니스 로직, 출력 |
| Controller | 비즈니스 로직, 상태 전이 | `print()`, `input()` 직접 호출 |
| View | `input()` 수집, `print()` 출력, 화면 렌더링 | 비즈니스 로직 |

### 6.3 모델 정의

**`Sample`**
```python
sample_id: str        # e.g. "S-001"
name: str
avg_production_time: float   # 분/ea
yield_rate: float     # 0.0 ~ 1.0
stock: int            # 현재 재고
```

**`OrderStatus`** (enum)
```python
RESERVED, REJECTED, PRODUCING, CONFIRMED, RELEASED
```

**`Order`**
```python
order_no: str         # e.g. "ORD-20260508-0001"
sample_id: str
customer: str
quantity: int
status: OrderStatus
created_at: datetime
```

**`ProductionJob`**
```python
order_no: str
sample_id: str
shortage: int         # 부족분 = 주문수량 - 재고
actual_qty: int       # ceil(shortage / (yield_rate * 0.9))
total_time: float     # avg_production_time * actual_qty (분)
```

### 6.4 컨트롤러 인터페이스

**`SampleController`**
```python
register(sample_id, name, avg_time, yield_rate) -> Sample
list_all() -> list[Sample]
search(keyword) -> list[Sample]
```

**`OrderController`**
```python
reserve(sample_id, customer, quantity) -> Order
approve(order_no) -> Order          # CONFIRMED 또는 PRODUCING
reject(order_no) -> Order           # REJECTED
release(order_no) -> Order          # RELEASED
list_reserved() -> list[Order]
list_confirmed() -> list[Order]
```

**`ProductionController`**
```python
enqueue(order_no) -> ProductionJob
get_current() -> ProductionJob | None
get_queue() -> list[ProductionJob]
```

**`MonitoringController`**
```python
get_order_stats() -> dict[OrderStatus, int]
get_inventory_status() -> list[dict]   # 시료별 재고 + 상태(여유/부족/고갈)
```

### 6.5 데이터 공유 (InMemoryStore)

모든 컨트롤러는 `InMemoryStore` 단일 인스턴스를 생성 시 주입받아 데이터를 공유한다.

```python
class InMemoryStore:
    samples: dict[str, Sample]
    orders: dict[str, Order]
    production_queue: deque[ProductionJob]
    current_job: ProductionJob | None
```

### 6.6 앱 라우팅 흐름

```
main.py
  └── App(store, controllers, views)
        └── run()
              └── 루프
                    ├── MainView.show_header(summary)
                    ├── MainView.show_menu()
                    ├── MainView.get_choice()
                    └── 선택에 따라 Controller + View 조합 실행
```

---

## 7. 핵심 비즈니스 로직 요약

| 로직 | 수식 |
|------|------|
| 실 생산량 | `ceil(부족분 / (수율 × 0.9))` |
| 총 생산 시간 | `평균 생산시간 × 실 생산량` |
| 부족분 | `주문 수량 - 현재 재고` |
| 재고 상태 | 고갈: 재고=0 / 부족: 재고<주문대비 / 여유: 그 외 |

---

## 8. 스켈레톤 범위 정의

이 PoC는 **구조 증명**이 목적이다. 아래 기준으로 구현 수준을 제한한다.

| 항목 | 포함 | 제외 |
|------|------|------|
| M/V/C 계층 분리 | ✅ | |
| 6개 메뉴 전체 골격 | ✅ | |
| 핵심 비즈니스 로직 (approve, 생산량 계산) | ✅ | |
| 데이터 영속성 | | ✅ (별도 PoC) |
| 실시간 생산 시뮬레이션 | | ✅ |
| 입력 유효성 검사 (엣지 케이스) | | ✅ |
| 테스트 코드 | | ✅ (미션2) |
