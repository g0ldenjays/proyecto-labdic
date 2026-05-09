from __future__ import annotations

import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from app.models.inventory import Device


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "report"
TEMPLATE_FILE = TEMPLATE_DIR / "main.tex"


def latex_escape(value: str | None) -> str:
    if not value:
        return "—"

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    escaped = value
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)

    return escaped.replace("\n", r"\\ ")


def build_device_rows(devices: Sequence[Device]) -> str:
    rows: list[str] = []

    for device in devices:
        rows.append(
            " & ".join(
                [
                    latex_escape(device.product.name if device.product else None),
                    latex_escape(device.product.category.name if device.product and device.product.category else None),
                    latex_escape(device.internal_code),
                    latex_escape(device.serial_number),
                    latex_escape(device.status.name if device.status else None),
                    latex_escape(device.ubication.name if device.ubication else None),
                ]
            )
            + r" \\ \hline"
        )

    return "\n".join(rows) if rows else r"Sin datos & — & — & — & — & — \\ \hline"


def render_inventory_report_tex(
    devices: Sequence[Device],
    search_label: str,
    status_label: str,
    ubication_label: str,
    category_label: str,
) -> str:
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    now = datetime.now(timezone.utc)

    content = template
    content = content.replace("@@DATE@@", now.strftime("%d/%m/%Y"))
    content = content.replace("@@TOTAL_DEVICES@@", str(len(devices)))
    content = content.replace("@@FILTER_SEARCH@@", latex_escape(search_label))
    content = content.replace("@@FILTER_STATUS@@", latex_escape(status_label))
    content = content.replace("@@FILTER_UBICATION@@", latex_escape(ubication_label))
    content = content.replace("@@FILTER_CATEGORY@@", latex_escape(category_label))
    content = content.replace("@@DEVICE_ROWS@@", build_device_rows(devices))
    return content


def _copy_images(workdir: Path) -> None:
    source_images = TEMPLATE_DIR / "images"
    target_images = workdir / "images"
    target_images.mkdir(parents=True, exist_ok=True)

    logo_umag = source_images / "logo_umag.png"
    if not logo_umag.exists():
        raise RuntimeError(
            f"No se encontró el logo requerido: {logo_umag}. "
            "Debes copiar logo_umag.png a templates/report/images/."
        )

    shutil.copy2(logo_umag, target_images / "logo_umag.png")


def compile_latex_to_pdf(workdir: Path) -> bytes:
    main_tex = workdir / "main.tex"

    tectonic = shutil.which("tectonic")
    if tectonic:
        result = subprocess.run(
            [tectonic, str(main_tex), "--outdir", str(workdir)],
            cwd=workdir,
            capture_output=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("latin-1", errors="replace")
            stdout = result.stdout.decode("latin-1", errors="replace")
            raise RuntimeError(
                "Error compilando PDF con tectonic.\n\nSTDERR:\n"
                f"{stderr}\n\nSTDOUT:\n{stdout}"
            )

        pdf_path = workdir / "main.pdf"
        if not pdf_path.exists():
            raise RuntimeError("La compilación terminó, pero no se encontró main.pdf")
        return pdf_path.read_bytes()

    pdflatex = shutil.which("pdflatex")
    if pdflatex:
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=workdir,
            capture_output=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("latin-1", errors="replace")
            stdout = result.stdout.decode("latin-1", errors="replace")
            raise RuntimeError(
                "Error compilando PDF con pdflatex.\n\nSTDERR:\n"
                f"{stderr}\n\nSTDOUT:\n{stdout}"
            )

        pdf_path = workdir / "main.pdf"
        if not pdf_path.exists():
            raise RuntimeError("La compilación terminó, pero no se encontró main.pdf")
        return pdf_path.read_bytes()

    raise RuntimeError(
        "No se encontró compilador LaTeX. Instala 'tectonic' o 'pdflatex' en el entorno."
    )


def build_inventory_report_pdf(
    devices: Sequence[Device],
    search_label: str,
    status_label: str,
    ubication_label: str,
    category_label: str,
) -> bytes:
    if not TEMPLATE_FILE.exists():
        raise RuntimeError(f"No se encontró la plantilla LaTeX: {TEMPLATE_FILE}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        workdir = Path(tmp_dir)

        _copy_images(workdir)

        rendered = render_inventory_report_tex(
            devices=devices,
            search_label=search_label,
            status_label=status_label,
            ubication_label=ubication_label,
            category_label=category_label,
        )
        (workdir / "main.tex").write_text(rendered, encoding="utf-8")

        return compile_latex_to_pdf(workdir)