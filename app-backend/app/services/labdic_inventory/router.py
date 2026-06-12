# app/services/labdic_inventory/router.py

from litestar import Router

from .auth.controllers import AuthController
from .catalog.controllers import (
    BrandController,
    CategoryController,
    ModelController,
    StatusController,
    UbicationController,
)
from .device.controllers import DeviceController
from .loan.controllers import LoanRequestController
from .product.controllers import ProductController
from .role.controllers import RoleController
from .user.controllers import UserController
from .inventory_admin import InventoryAdminController
from .book.controllers import BookController

labdic_inventory_router = Router(
    path="/labdic_inventory",
    route_handlers=[
        UserController,
        RoleController,
        AuthController,
        ProductController,
        BrandController,
        CategoryController,
        ModelController,
        StatusController,
        UbicationController,
        DeviceController,
        LoanRequestController,
        InventoryAdminController,
        BookController,
    ],
)
