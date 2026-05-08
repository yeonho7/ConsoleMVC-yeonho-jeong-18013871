# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

반도체 시료 생산주문관리 시스템의 **MVC 스켈레톤 코드 PoC** (Proof of Concept).  
Python 콘솔 기반 대화형 앱으로, Model / Controller / View 계층 분리를 증명하는 것이 목적이다.  
상세 요구사항은 `docs/PRD.md`, 구현 계획은 `docs/PLAN.md` 참조.

## 실행 명령어

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 앱 실행
python main.py
```

외부 의존성 없음. 표준 라이브러리만 사용 (`math`, `datetime`, `collections.deque`, `dataclasses`, `enum`).

## 아키텍처

```
main.py  →  src/app.py (메인 루프 + 라우터)
                ├── src/store.py          InMemoryStore — 모든 데이터 공유 저장소
                ├── src/models/           순수 데이터 클래스
                ├── src/controllers/      비즈니스 로직
                └── src/views/            입출력(input/print) 전담
```

**데이터 흐름**: `View`가 사용자 입력을 수집해 `Controller`에 전달 → `Controller`가 `Store`를 읽고 쓰며 상태 전이 → 결과 데이터를 `View`에 반환 → `View`가 출력.

## 계층별 책임 규칙

| 계층 | 해야 할 것 | 하면 안 되는 것 |
|------|-----------|----------------|
| Model | 데이터 구조, 상태 보유 | 비즈니스 로직, 출력 |
| Controller | 비즈니스 로직, 상태 전이, Store 읽기/쓰기 | `print()`, `input()` 직접 호출 |
| View | `input()` 수집, `print()` 출력 | 비즈니스 로직, Store 직접 접근 |

## 핵심 도메인

**주문 상태 전이**:
```
RESERVED → (승인 + 재고 충분) → CONFIRMED → RELEASED
RESERVED → (승인 + 재고 부족) → PRODUCING → CONFIRMED → RELEASED
RESERVED → (거절)             → REJECTED
```

**생산량 계산** (`order_controller.py`의 `approve` 메서드):
```python
shortage   = quantity - sample.stock
actual_qty = math.ceil(shortage / (sample.yield_rate * 0.9))
total_time = sample.avg_production_time * actual_qty
```

**재고 상태 판정** (`monitoring_controller.py`):
- 고갈: `stock == 0`
- 부족: 해당 시료의 RESERVED + PRODUCING 주문 합계 > stock
- 여유: 그 외

## InMemoryStore

`src/store.py`의 `InMemoryStore` 단일 인스턴스가 `App.__init__`에서 생성되고 모든 Controller에 주입된다. Controller끼리 직접 참조하지 않고 Store를 통해서만 데이터를 공유한다.

```python
store.samples           # dict[str, Sample]       key=sample_id
store.orders            # dict[str, Order]         key=order_no
store.production_queue  # deque[ProductionJob]     FIFO
store.current_job       # ProductionJob | None
```

## 주문번호 형식

`ORD-YYYYMMDD-XXXX` (예: `ORD-20260508-0001`) — `store.next_order_no()`가 발급.

## 스켈레톤 범위

이 PoC는 **구조 증명**이 목적이므로 아래는 구현하지 않는다:
- 데이터 영속성 (별도 DataPersistence PoC)
- 실시간 생산 시뮬레이션
- 엣지 케이스 입력 유효성 검사
- 테스트 코드 (미션2에서 작성)
