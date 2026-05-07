# app/services/labdic_inventory/device/dtos.py

from dataclasses import dataclass

from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig
from litestar.plugins.sqlalchemy import SQLAlchemyDTO

from app.models.inventory import Device, DeviceStatusLog


# --- Device ---
class DeviceReadDTO(SQLAlchemyDTO[Device]):
    config = SQLAlchemyDTOConfig(
        exclude={"loan_request_items", "status_logs", "administrative_document_items"},
        partial=True,
    )

class DeviceCreateDTO(SQLAlchemyDTO[Device]):
    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "loan_request_items", "status_logs", "product", "status", "ubication", "administrative_document_items"},
        partial=False,
    )

class DeviceUpdateDTO(SQLAlchemyDTO[Device]):
    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "status_id", "loan_request_items", "status_logs", "product", "status", "ubication", "administrative_document_items"},
        partial=True,
    )


# --- Payload para cambio de estado ---
@dataclass
class DeviceStatusChangeDTO:
    """Payload para el endpoint PATCH /devices/{id}/status."""
    status_id: int


# --- DeviceStatusLog ---
class DeviceStatusLogReadDTO(SQLAlchemyDTO[DeviceStatusLog]):
    config = SQLAlchemyDTOConfig(
        # Solo lectura: se excluyen las relaciones pesadas, se exponen status y user resumidos
        exclude={"device"},
        partial=True,
    )