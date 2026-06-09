# app/services/labdic_inventory/loan/dtos.py

from dataclasses import dataclass
from datetime import datetime

from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig
from litestar.plugins.sqlalchemy import SQLAlchemyDTO

from app.models.inventory import LoanRequest

class LoanRequestReadDTO(SQLAlchemyDTO[LoanRequest]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "user.password",
            "user.roles", 
            "user.loan_requests",
            "user.status_logs",
            "loan_request_items.loan_request",
            "loan_request_items.device.loan_request_items",
            "loan_request_items.device.status_logs",
            "loan_request_items.device.product.devices",
        },
        partial=True,
    )

@dataclass
class LoanRequestCreateDTO:
    """Payload para crear una solicitud de préstamo con sus devices."""
    device_ids: list[int]
    reason: str | None = None
    estimated_return_date: datetime | None = None
    requested_user_id: int | None = None