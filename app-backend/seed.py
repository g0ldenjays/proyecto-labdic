# app-backend/seed.py

from datetime import datetime, timezone

from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.inventory import (
    Brand,
    Category,
    Device,
    DeviceStatusLog,
    LoanRequest,
    LoanRequestItem,
    Model,
    Product,
    Role,
    Status,
    Ubication,
    User,
    UserRole,
)

engine = create_engine(settings.database_url.unicode_string())
password_hasher = PasswordHash.recommended()

"""
Este archivo seed.py se encarga de poblar la base de datos con datos iniciales para los modelos básicos del sistema de inventario del LabDIC.

Modelos que ya están listos (con sus dependencias):

- Role: No depende de otros modelos. Define los roles de usuario (administrador, usuario, técnico).

- Status: No depende de otros modelos. Define los estados posibles para dispositivos y solicitudes de préstamo.

- Brand: No depende de otros modelos. Define las marcas de productos (Dell, HP, etc.).

- Model: No depende de otros modelos. Define los modelos de productos (XPS 13, Spectre x360, etc.).

- Category: No depende de otros modelos. Define las categorías de productos (Laptop, Tablet, etc.).

- Ubication: No depende de otros modelos. Define las ubicaciones físicas de los dispositivos (TI-1, TI-2, etc.).

Modelos que aún no están agregados a esta semilla:

- User: Depende de Role (a través de la tabla intermedia user_roles). Los usuarios se crean dinámicamente o mediante registro.

- Product: Depende de Brand, Model y Category. Los productos se definen según el inventario específico.

- Device: Depende de Product, Status y Ubication. Los dispositivos son instancias físicas de productos.

- LoanRequest: Depende de User y Status. Las solicitudes de préstamo se crean por usuarios.

- LoanRequestItem: Depende de LoanRequest y Device. Elementos individuales de solicitudes.

- DeviceStatusLog: Depende de Device, Status y User. Registros de cambios de estado.

Estos modelos no se siembran aquí porque requieren datos específicos o se generan dinámicamente durante el uso del sistema.
"""

def clear_db(session: Session) -> None:
    session.query(DeviceStatusLog).delete()   # depende de Device, User, Status
    session.query(LoanRequestItem).delete()   # depende de LoanRequest, Device
    session.query(LoanRequest).delete()       # depende de User, Status
    session.query(Device).delete()            # depende de Product, Status, Ubication
    session.query(UserRole).delete()          # depende de User, Role
    session.query(Product).delete()           # depende de Brand, Model, Category
    session.query(User).delete()              # depende de Role (via UserRole, ya limpia)
    session.query(Role).delete()              # sin dependencias hijas
    session.query(Status).delete()            # sin dependencias hijas
    session.query(Brand).delete()             # sin dependencias hijas
    session.query(Model).delete()             # sin dependencias hijas
    session.query(Category).delete()          # sin dependencias hijas
    session.query(Ubication).delete()         # sin dependencias hijas
    session.flush()
    print("  🗑️  Base de datos limpiada\n")

# --- NIVEL 1 ---
# Sin dependencias.

def seed_roles(session: Session) -> list[Role]:
    roles = [
        Role(name="administrador", description="Acceso total al sistema"),
        Role(name="usuario", description="Acceso estándar para solicitar préstamos"),
        Role(name="técnico", description="Gestión de dispositivos y mantenimiento"),
    ]
    session.add_all(roles)
    print("  ✓ Roles insertados")
    return roles


def seed_statuses(session: Session) -> None:
    statuses = [
        # Estados de dispositivos
        Status(name="disponible"),
        Status(name="prestado"),
        Status(name="en_mantenimiento"),
        Status(name="entregado"),
        Status(name="devuelto"),
        Status(name="de_baja"),
        # Estados de solicitudes
        Status(name="pendiente"),
        Status(name="aprobado"),
        Status(name="rechazado"),
    ]
    session.add_all(statuses)
    print("  ✓ Statuses insertados")


def seed_brands(session: Session) -> None:
    brands = [
        Brand(name="Dell"),
        Brand(name="HP"),
        Brand(name="Apple"),
        Brand(name="Lenovo"),
        Brand(name="Asus"),
        Brand(name="Acer"),
        Brand(name="Samsung"),
        Brand(name="Logitech"),
    ]
    session.add_all(brands)
    print("  ✓ Brands insertados")


def seed_models(session: Session) -> None:
    models = [
        Model(name="XPS 13"),
        Model(name="Spectre x360"),
        Model(name="MacBook Pro"),
        Model(name="ThinkPad X1 Carbon"),
        Model(name="ZenBook 14"),
        Model(name="Aspire 5"),
        Model(name="EliteBook 840"),
        Model(name="Galaxy Tab S8"),
    ]
    session.add_all(models)
    print("  ✓ Models insertados")


def seed_categories(session: Session) -> None:
    categories = [
        Category(name="Laptop"),
        Category(name="Tablet"),
        Category(name="Smartphone"),
        Category(name="Monitor"),
        Category(name="Teclado"),
        Category(name="Mouse"),
        Category(name="Proyector"),
        Category(name="Cable"),
        Category(name="Adaptador"),
    ]
    session.add_all(categories)
    print("  ✓ Categories insertadas")


def seed_ubications(session: Session) -> None:
    ubications = [
        Ubication(name="TI-1", description="Sala principal de computadoras"),
        Ubication(name="TI-2", description="Sala secundaria de computadoras"),
        Ubication(name="Redes", description="Sala de equipos de redes"),
        Ubication(name="Administración", description="Oficina administrativa del LabDIC"),
        Ubication(name="Bodega", description="Almacenamiento de equipos en desuso o mantención"),
    ]
    session.add_all(ubications)
    print("  ✓ Ubications insertadas")

# --- NIVEL 2 ---

def seed_users(session: Session, roles: list[Role]) -> None:
    # Buscar roles por nombre para asignarlos
    rol_admin = next(r for r in roles if r.name == "administrador")
    rol_usuario = next(r for r in roles if r.name == "usuario")
    rol_tecnico = next(r for r in roles if r.name == "técnico")

    users = [
        User(
            rut="21021646-4",
            name="Ariel López",
            username="admin",
            email="arilopez@umag.cl",
            password=password_hasher.hash("admin"),
            phone="+56941394363",
            address="Punta Arenas",
            created_at=datetime.now(timezone.utc),
            is_active=True,
            is_admin=True,
            roles=[rol_admin],
        ),
        User(
            rut="12345678-9",
            name="Juan Pérez",
            username="juanperez",
            email="juanperez@umag.cl",
            password=password_hasher.hash("usuario1234"),
            phone="+56912345678",
            address="Punta Arenas",
            created_at=datetime.now(timezone.utc),
            is_active=True,
            is_admin=False,
            roles=[rol_usuario],
        ),
        User(
            rut="98765432-1",
            name="María Gómez",
            username="mariagomez",
            email="mariagomez@umag.cl",
            password=password_hasher.hash("tecnico1234"),
            phone="+56987654321",
            address="Punta Arenas",
            created_at=datetime.now(timezone.utc),
            is_active=True,
            is_admin=False,
            roles=[rol_tecnico],
        ),
    ]
    session.add_all(users)
    print("  ✓ Users insertados")


def seed_products(session: Session) -> None:

    with session.no_autoflush:  # ← evita el autoflush durante la construcción
        def get_brand(name: str) -> Brand:
            return session.query(Brand).filter_by(name=name).one()

        def get_model(name: str) -> Model:
            return session.query(Model).filter_by(name=name).one()

        def get_category(name: str) -> Category:
            return session.query(Category).filter_by(name=name).one()

        products = [
            Product(
                name="Laptop Dell XPS 13",
                brand=get_brand("Dell"),
                model=get_model("XPS 13"),
                category=get_category("Laptop"),
                description="Laptop ultradelgada para uso general en el laboratorio.",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            Product(
                name="Laptop HP EliteBook 840",
                brand=get_brand("HP"),
                model=get_model("EliteBook 840"),
                category=get_category("Laptop"),
                description="Laptop empresarial de alto rendimiento.",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            Product(
                name="Laptop Lenovo ThinkPad X1 Carbon",
                brand=get_brand("Lenovo"),
                model=get_model("ThinkPad X1 Carbon"),
                category=get_category("Laptop"),
                description="Laptop liviana orientada a productividad.",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
            Product(
                name="Tablet Samsung Galaxy Tab S8",
                brand=get_brand("Samsung"),
                model=get_model("Galaxy Tab S8"),
                category=get_category("Tablet"),
                description="Tablet para presentaciones y uso móvil.",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ),
        ]
        session.add_all(products)

    print("  ✓ Products insertados")

# --- NIVEL 3 ---

def seed_devices(session: Session) -> list[Device]:
    def get_product(name: str) -> Product:
        return session.query(Product).filter_by(name=name).one()

    def get_status(name: str) -> Status:
        return session.query(Status).filter_by(name=name).one()

    def get_ubication(name: str) -> Ubication:
        return session.query(Ubication).filter_by(name=name).one()

    with session.no_autoflush:
        devices = [
            # Laptop Dell XPS 13 — 2 unidades
            Device(
                product=get_product("Laptop Dell XPS 13"),
                internal_code="DELL-XPS-001",
                serial_number="SN-DXPS-001",
                status=get_status("disponible"),
                ubication=get_ubication("TI-1"),
                created_at=datetime.now(timezone.utc),
            ),
            Device(
                product=get_product("Laptop Dell XPS 13"),
                internal_code="DELL-XPS-002",
                serial_number="SN-DXPS-002",
                status=get_status("disponible"),
                ubication=get_ubication("TI-1"),
                created_at=datetime.now(timezone.utc),
            ),
            # Laptop HP EliteBook 840 — 2 unidades
            Device(
                product=get_product("Laptop HP EliteBook 840"),
                internal_code="HP-ELB-001",
                serial_number="SN-HELB-001",
                status=get_status("disponible"),
                ubication=get_ubication("TI-2"),
                created_at=datetime.now(timezone.utc),
            ),
            Device(
                product=get_product("Laptop HP EliteBook 840"),
                internal_code="HP-ELB-002",
                serial_number="SN-HELB-002",
                status=get_status("disponible"),
                ubication=get_ubication("TI-2"),
                created_at=datetime.now(timezone.utc),
            ),
            # Laptop Lenovo ThinkPad X1 Carbon — 2 unidades
            Device(
                product=get_product("Laptop Lenovo ThinkPad X1 Carbon"),
                internal_code="LEN-TPX1-001",
                serial_number="SN-LTPX1-001",
                status=get_status("disponible"),
                ubication=get_ubication("TI-1"),
                created_at=datetime.now(timezone.utc),
            ),
            Device(
                product=get_product("Laptop Lenovo ThinkPad X1 Carbon"),
                internal_code="LEN-TPX1-002",
                serial_number="SN-LTPX1-002",
                status=get_status("disponible"),
                ubication=get_ubication("TI-2"),
                created_at=datetime.now(timezone.utc),
            ),
            # Tablet Samsung Galaxy Tab S8 — 2 unidades
            Device(
                product=get_product("Tablet Samsung Galaxy Tab S8"),
                internal_code="SAM-GTS8-001",
                serial_number="SN-SGTS8-001",
                status=get_status("disponible"),
                ubication=get_ubication("Administración"),
                created_at=datetime.now(timezone.utc),
            ),
            Device(
                product=get_product("Tablet Samsung Galaxy Tab S8"),
                internal_code="SAM-GTS8-002",
                serial_number="SN-SGTS8-002",
                status=get_status("disponible"),
                ubication=get_ubication("Administración"),
                created_at=datetime.now(timezone.utc),
            ),
        ]
        session.add_all(devices)

    print("  ✓ Devices insertados")
    return devices


# --- NIVEL 4 ---

def seed_loans(session: Session, devices: list[Device]) -> None:
    def get_user(username: str) -> User:
        return session.query(User).filter_by(username=username).one()

    def get_status(name: str) -> Status:
        return session.query(Status).filter_by(name=name).one()

    with session.no_autoflush:
        usuario = get_user("juanperez")
        print(f"  → Usuario encontrado: {usuario.name}")

        # Préstamo 1 — pendiente (1 Dell XPS 13)
        loan_pendiente = LoanRequest(
            user=usuario,
            status=get_status("pendiente"),
            reason="Proyecto de redes semestre 1",
            estimated_return_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
            request_date=datetime.now(timezone.utc),
        )
        session.add(loan_pendiente)
        session.flush()
        session.add(LoanRequestItem(loan_request=loan_pendiente, device=devices[0]))
        print("  → Préstamo #1 creado: estado='pendiente'")
        print(f"     - Item: {devices[0].internal_code} ({devices[0].serial_number})")

        # Préstamo 2 — aprobado (1 HP EliteBook)
        loan_aprobado = LoanRequest(
            user=usuario,
            status=get_status("aprobado"),
            reason="Taller de programación",
            estimated_return_date=datetime(2026, 4, 15, tzinfo=timezone.utc),
            request_date=datetime.now(timezone.utc),
        )
        session.add(loan_aprobado)
        session.flush()
        session.add(LoanRequestItem(loan_request=loan_aprobado, device=devices[2]))
        print("  → Préstamo #2 creado: estado='aprobado'")
        print(f"     - Item: {devices[2].internal_code} ({devices[2].serial_number})")

        # Préstamo 3 — prestado/entregado (1 Lenovo ThinkPad)
        devices[4].status = get_status("prestado")
        print(f"  → Device actualizado a 'prestado': {devices[4].internal_code}")
        loan_prestado = LoanRequest(
            user=usuario,
            status=get_status("prestado"),
            reason="Presentación de proyecto final",
            estimated_return_date=datetime(2026, 3, 20, tzinfo=timezone.utc),
            request_date=datetime.now(timezone.utc),
            delivery_date=datetime.now(timezone.utc),
        )
        session.add(loan_prestado)
        session.flush()
        session.add(LoanRequestItem(loan_request=loan_prestado, device=devices[4]))
        print("  → Préstamo #3 creado: estado='prestado'")
        print(f"     - Item: {devices[4].internal_code} ({devices[4].serial_number})")
        print(f"     - Entregado el: {loan_prestado.delivery_date.strftime('%Y-%m-%d %H:%M')}")

    print("  ✓ Loans insertados")

def run() -> None:
    print("\n🌱 Iniciando seed de la base de datos...\n")
    with Session(engine) as session:
        try:
            clear_db(session)

            # Nivel 1 — sin dependencias
            roles = seed_roles(session)
            seed_statuses(session)
            seed_brands(session)
            seed_models(session)
            seed_categories(session)
            seed_ubications(session)
            session.flush()

            # Nivel 2 — depende del nivel 1
            seed_users(session, roles)
            seed_products(session)
            session.flush()

            # Nivel 3 — depende del nivel 2
            devices = seed_devices(session)
            session.flush()

            # Nivel 4 — depende del nivel 3
            seed_loans(session, devices)

            session.commit()
            print("\n✅ Seed completado exitosamente.\n")
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error durante el seed, rollback ejecutado: {e}\n")
            raise

if __name__ == "__main__":
    run()
