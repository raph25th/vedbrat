import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree

PLACEHOLDER_RE = re.compile(r"\$\{([a-zA-Z0-9_.]+)\}")


class DocumentTemplateError(ValueError):
    pass


class DocumentTemplateService:
    def extract_variables_from_docx(self, file_path: str | Path) -> list[str]:
        path = Path(file_path)
        if not path.exists():
            return []

        text_chunks: list[str] = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.startswith("word/") and name.endswith(".xml"):
                    xml_bytes = archive.read(name)
                    try:
                        root = ElementTree.fromstring(xml_bytes)
                    except ElementTree.ParseError:
                        continue
                    text_chunks.extend(node.text or "" for node in root.iter() if node.text)

        # TODO: for production use an OOXML-safe parser. DOCX variables can be split across runs.
        variables = PLACEHOLDER_RE.findall("".join(text_chunks))
        return sorted(set(variables))

    def render_docx(self, template_path: str | Path, context: dict, output_dir: str | Path) -> Path:
        source = Path(template_path)
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"generated-{source.stem}.docx"

        if not source.exists():
            raise FileNotFoundError(str(source))

        shutil.copyfile(source, target)
        replacements = {f"${{{key}}}": str(value) for key, value in context.items()}

        if not replacements:
            return target

        tmp_target = target.with_suffix(".tmp.docx")
        with zipfile.ZipFile(target, "r") as source_zip, zipfile.ZipFile(tmp_target, "w") as output_zip:
            for item in source_zip.infolist():
                data = source_zip.read(item.filename)
                if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                    text = data.decode("utf-8")
                    for placeholder, value in replacements.items():
                        text = text.replace(placeholder, value)
                    data = text.encode("utf-8")
                output_zip.writestr(item, data)

        tmp_target.replace(target)
        # TODO: this preserves XML structure for same-run placeholders; split-run variables need robust OOXML replacement.
        return target

    def unresolved_variables_in_docx(self, file_path: str | Path) -> list[str]:
        return self.extract_variables_from_docx(file_path)

    def convert_docx_to_pdf(self, docx_path: str | Path, output_dir: str | Path | None = None) -> Path:
        source = Path(docx_path)
        if not source.exists():
            raise DocumentTemplateError(f"DOCX file not found: {source}")

        target_dir = Path(output_dir) if output_dir else source.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        executable = shutil.which("soffice") or shutil.which("libreoffice")
        if not executable:
            raise DocumentTemplateError(
                "Не найден LibreOffice/soffice для конвертации DOCX в PDF. "
                "Установите LibreOffice на сервер и убедитесь, что команда soffice или libreoffice доступна в PATH."
            )

        result = subprocess.run(
            [
                executable,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(target_dir),
                str(source),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        pdf_path = target_dir / f"{source.stem}.pdf"
        if result.returncode != 0 or not pdf_path.exists():
            detail = (result.stderr or result.stdout or "unknown LibreOffice error").strip()
            raise DocumentTemplateError(f"Не удалось конвертировать DOCX в PDF: {detail}")
        return pdf_path
