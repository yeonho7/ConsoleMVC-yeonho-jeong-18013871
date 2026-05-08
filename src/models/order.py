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
