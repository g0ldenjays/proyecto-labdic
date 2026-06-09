# Parche 1.2
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

"""plataforma web desarrollada para gestionar los préstamos de materiales y
dispositivos en el Laboratorio del Departamento de Ingeniería en Computación (LabDIC)."""


# Tabla intermedia para la relación M-M entre usuarios y roles
class UserRole(Base):
    """Tabla intermedia entre usuarios y roles."""

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)

class User(Base):
    """Control de acceso y autenticación de usuarios."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    rut: Mapped[str] = mapped_column(String(12), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    phone: Mapped[str] = mapped_column(String(18), nullable=True)
    address: Mapped[str] = mapped_column(String(360), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)

    roles: Mapped[list["Role"]] = relationship("Role", secondary="user_roles", back_populates="users")
    loan_requests: Mapped[list["LoanRequest"]] = relationship("LoanRequest", back_populates="user")
    status_logs: Mapped[list["DeviceStatusLog"]] = relationship("DeviceStatusLog", back_populates="user")
    administrative_documents: Mapped[list["AdministrativeDocument"]] = relationship("AdministrativeDocument", back_populates="generated_by_user")

class Role(Base):
    """Role model for user roles in the system."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship("User", secondary="user_roles", back_populates="roles")

class Brand(Base):
    """Brand model for product brands."""

    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True) # Ejemplo: "Dell, HP, Apple"

    products: Mapped[list["Product"]] = relationship("Product", back_populates="brand")

class Model(Base):
    """Model model for product models."""

    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True) # Ejemplo: "XPS 13, Spectre x360, MacBook Pro"

    products: Mapped[list["Product"]] = relationship("Product", back_populates="model")

class Category(Base):
    """Category model for product categories."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True) # Ejemplo: "Laptops, Tablets, Smartphones"

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

class Product(Base):
    """Representa un tipo de producto del inventario (ej: Notebook, Arduino Uno).

    Cada Product puede tener múltiples Device asociados,
    donde cada Device es una unidad física individual.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Ejemplo: "Laptop Dell XPS 13"
    name: Mapped[str] = mapped_column(String(100), unique=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"), nullable=True)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("models.id"), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    model: Mapped["Model"] = relationship("Model", back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")


class Status(Base):
    """Para gestionar los estados de los dispositivos y solicitudes."""

    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Ejemplo: "available, borrowed, under_maintenance, pending, approved, rejected"
    name: Mapped[str] = mapped_column(String(50), unique=True)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="status")
    loan_requests: Mapped[list["LoanRequest"]] = relationship("LoanRequest", back_populates="status")
    status_logs: Mapped[list["DeviceStatusLog"]] = relationship("DeviceStatusLog", back_populates="status")

class Ubication(Base):
    """Para gestionar las ubicaciones de los dispositivos."""

    __tablename__ = "ubications"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Ejemplo: "TI-1, TI-2, Redes, Administración, etc."
    name: Mapped[str] = mapped_column(String(100), unique=True)
    # Ejemplo: "Sala equipada con 20 computadoras"
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="ubication")

    source_documents: Mapped[list["AdministrativeDocument"]] = relationship("AdministrativeDocument", foreign_keys="AdministrativeDocument.source_ubication_id", back_populates="source_ubication")
    target_documents: Mapped[list["AdministrativeDocument"]] = relationship("AdministrativeDocument", foreign_keys="AdministrativeDocument.target_ubication_id", back_populates="target_ubication")

class Device(Base):
    """Para administrar cada elemento del inventario."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    # Ejemplo: "7467122111293"
    internal_code: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    # Ejemplo: "SN123456789"
    serial_number: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    ubication_id: Mapped[int | None] = mapped_column(ForeignKey("ubications.id"), nullable=True)

    # Relación con Product, Status y Ubication
    product: Mapped["Product"] = relationship("Product", back_populates="devices")
    status: Mapped["Status"] = relationship("Status", back_populates="devices")
    ubication: Mapped["Ubication"] = relationship("Ubication", back_populates="devices")
    loan_request_items: Mapped[list["LoanRequestItem"]] = relationship(
    "LoanRequestItem",
    back_populates="device",
    cascade="all, delete-orphan",
    passive_deletes=True,
    )

    status_logs: Mapped[list["DeviceStatusLog"]] = relationship("DeviceStatusLog", back_populates="device")
    administrative_document_items: Mapped[list["AdministrativeDocumentItem"]] = relationship(
    "AdministrativeDocumentItem",
    back_populates="device",
    cascade="all, delete-orphan",
    passive_deletes=True,
    )
    observation: Mapped[str | None] = mapped_column(Text, nullable=True)

class LoanRequest(Base):
    """Para gestionar las solicitudes de préstamo de dispositivos."""

    __tablename__ = "loan_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    request_date: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    # Relación con Status
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    # Ejemplo: "Necesito el dispositivo para un proyecto"
    reason: Mapped[str] = mapped_column(String(500), nullable=True)
    # Fecha de entrega del dispositivo
    delivery_date: Mapped[datetime] = mapped_column(nullable=True)
    # Fecha estimada de devolución del dispositivo
    estimated_return_date: Mapped[datetime] = mapped_column(nullable=True)
    # Fecha real de devolución del dispositivo
    actual_return_date: Mapped[datetime] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="loan_requests")
    status: Mapped["Status"] = relationship("Status", back_populates="loan_requests")
    loan_request_items: Mapped[list["LoanRequestItem"]] = relationship(
        "LoanRequestItem",
        back_populates="loan_request",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
class LoanRequestItem(Base):
    """Para gestionar los elementos de las solicitudes de préstamo, individualmente."""

    __tablename__ = "loan_request_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    loan_request_id: Mapped[int] = mapped_column(
        ForeignKey("loan_requests.id", ondelete="CASCADE")
    )
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE")
    )

    loan_request: Mapped["LoanRequest"] = relationship("LoanRequest", back_populates="loan_request_items")
    device: Mapped["Device"] = relationship("Device", back_populates="loan_request_items")

class DeviceStatusLog(Base):
    """Para registrar los cambios de estado de los dispositivos."""

    __tablename__ = "device_status_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    # Usuario que realizó el cambio
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="status_logs")
    device: Mapped["Device"] = relationship("Device", back_populates="status_logs")
    status: Mapped["Status"] = relationship("Status", back_populates="status_logs")

class AdministrativeDocument(Base):
    """Documento administrativo interno del inventario."""

    __tablename__ = "administrative_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_type: Mapped[str] = mapped_column(String(30))  # Dar de baja | traslado
    generated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    generated_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_ubication_id: Mapped[int | None] = mapped_column(
        ForeignKey("ubications.id"),
        nullable=True,
    )
    target_ubication_id: Mapped[int | None] = mapped_column(
        ForeignKey("ubications.id"),
        nullable=True,
    )

    snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    generated_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="administrative_documents",
    )

    source_ubication: Mapped["Ubication | None"] = relationship(
        "Ubication",
        foreign_keys=[source_ubication_id],
        back_populates="source_documents",
    )

    target_ubication: Mapped["Ubication | None"] = relationship(
        "Ubication",
        foreign_keys=[target_ubication_id],
        back_populates="target_documents",
    )

    items: Mapped[list["AdministrativeDocumentItem"]] = relationship(
        "AdministrativeDocumentItem",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AdministrativeDocumentItem(Base):
    """Dispositivos asociados a un documento administrativo."""

    __tablename__ = "administrative_document_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("administrative_documents.id", ondelete="CASCADE")
    )
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE")
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["AdministrativeDocument"] = relationship(
        "AdministrativeDocument",
        back_populates="items",
    )
    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="administrative_document_items",
    )