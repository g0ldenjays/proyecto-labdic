from __future__ import annotations

import shutil
import subprocess
import tempfile
from datetime import timezone
from pathlib import Path

from app.models.inventory import AdministrativeDocument


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "transfer"
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


def build_device_rows(document: AdministrativeDocument) -> str:
    devices = (document.snapshot or {}).get("devices", [])
    rows: list[str] = []

    for device in devices:
        rows.append(
            " & ".join(
                [
                    latex_escape(device.get("product")),
                    latex_escape(device.get("internal_code")),
                    latex_escape(device.get("serial_number")),
                    latex_escape(device.get("status")),
                    latex_escape(device.get("source_ubication")),
                ]
            )
            + r" \\ \hline"
        )

    return "\n".join(rows) if rows else r"Sin datos & — & — & — & — \\ \hline"


def render_transfer_tex(document: AdministrativeDocument) -> str:
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    generated_at = document.generated_at.astimezone(timezone.utc)

    source_name = document.source_ubication.name if document.source_ubication else "Múltiples ubicaciones"
    target_name = document.target_ubication.name if document.target_ubication else "—"

    content = template
    content = content.replace("@@DATE@@", generated_at.strftime("%d/%m/%Y"))
    content = content.replace("@@ORDER@@", str(document.id))
    content = content.replace(
        "@@RESPONSIBLE_NAME@@",
        latex_escape(document.generated_by_user.name if document.generated_by_user else "—"),
    )
    content = content.replace("@@SOURCE_UBICATION@@", latex_escape(source_name))
    content = content.replace("@@TARGET_UBICATION@@", latex_escape(target_name))
    content = content.replace("@@REASON@@", latex_escape(document.reason))
    content = content.replace("@@OBSERVATIONS@@", latex_escape(document.observations))
    content = content.replace("@@DEVICE_ROWS@@", build_device_rows(document))
    return content


def _copy_images(workdir: Path) -> None:
    source_images = TEMPLATE_DIR / "images"
    target_images = workdir / "images"
    target_images.mkdir(parents=True, exist_ok=True)

    logo_umag = source_images / "logo_umag.png"
    if not logo_umag.exists():
        raise RuntimeError(
            f"No se encontró el logo requerido: {logo_umag}. "
            "Debes copiar logo_umag.png a templates/transfer/images/."
        )

    shutil.copy2(logo_umag, target_images / "logo_umag.png")


def compile_latex_to_pdf(workdir: Path) -> bytes:
    main_tex = workdir / "main.tex"

    tectonic = shutil.which("tectonic")
    if tectonic:
        subprocess.run(
            [tectonic, str(main_tex), "--outdir", str(workdir)],
            cwd=workdir,
            check=True,
            capture_output=True,
            text=True,
        )
        return (workdir / "main.pdf").read_bytes()

    pdflatex = shutil.which("pdflatex")
    if pdflatex:
        subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=workdir,
            check=True,
            capture_output=True,
            text=True,
        )
        return (workdir / "main.pdf").read_bytes()

    raise RuntimeError(
        "No se encontró compilador LaTeX. Instala 'tectonic' o 'pdflatex' en el entorno."
    )


def build_transfer_pdf(document: AdministrativeDocument) -> bytes:
    if not TEMPLATE_FILE.exists():
        raise RuntimeError(
            f"No se encontró la plantilla LaTeX: {TEMPLATE_FILE}"
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        workdir = Path(tmp_dir)

        _copy_images(workdir)

        rendered = render_transfer_tex(document)
        (workdir / "main.tex").write_text(rendered, encoding="utf-8")

        return compile_latex_to_pdf(workdir)