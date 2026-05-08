from dataclasses import dataclass


@dataclass
class ProductionJob:
    order_no: str
    sample_id: str
    shortage: int
    actual_qty: int
    total_time: float
