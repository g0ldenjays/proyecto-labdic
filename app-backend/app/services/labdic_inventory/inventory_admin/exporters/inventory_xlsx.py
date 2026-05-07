from io import BytesIO
from typing import Sequence

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

from app.models.inventory import Device


def _autosize_columns(sheet: Worksheet) -> None:
    for column_cells in sheet.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, len(value))
        sheet.column_dimensions[column_letter].width = min(max_length + 2, 40)


def build_inventory_xlsx(devices: Sequence[Device]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"

    headers = [
        "ID",
        "Producto",
        "Categoría",
        "Código interno",
        "Número de serie",
        "Estado",
        "Ubicación",
    ]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    for device in devices:
        ws.append([
            device.id,
            device.product.name if device.product else "—",
            device.product.category.name if device.product and device.product.category else "—",
            device.internal_code or "—",
            device.serial_number or "—",
            device.status.name if device.status else "—",
            device.ubication.name if device.ubication else "—",
        ])

    _autosize_columns(ws)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()