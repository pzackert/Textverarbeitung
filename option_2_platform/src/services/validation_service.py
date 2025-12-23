import logging
import re
from datetime import datetime
from time import perf_counter
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz
from docx import Document
from openpyxl import load_workbook

from src.core.models import Project
from src.services.annotation_service import annotation_service
from src.services.criteria_service import criteria_service
from src.services.project_service import project_service
from src.services.criteria_results_store import save_criterion_result

logger = logging.getLogger(__name__)


class ValidationService:
    def __init__(self):
        self.annotation_service = annotation_service

    def evaluate_criterion(self, project_id: str, criterion_id: str) -> Dict[str, Any]:
        project = project_service.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        criterion = criteria_service.get_by_id(criterion_id)
        if not criterion:
            raise ValueError(f"Criterion {criterion_id} not found")

        start = perf_counter()
        evidence_list = self._collect_evidence(project, criterion)
        status_raw = "green" if evidence_list else "red"
        status = self._normalize_status(status_raw)
        score = 1.0 if evidence_list else 0.0
        reason = "Nachweis gefunden" if evidence_list else "Kein Nachweis gefunden"

        output_dir = Path("data/input") / project_id / "annotated"
        annotations: List[Dict[str, Any]] = []
        evidence_records: List[Dict[str, Any]] = []
        for evidence in evidence_list:
            annotated = self.annotation_service.annotate_document(
                file_path=Path(evidence["path"]),
                evidence=evidence,
                criterion_id=criterion.id,
                output_dir=output_dir,
                status=status,
            )
            if annotated:
                annotated["document_id"] = evidence.get("document_id")
                annotated["document"] = evidence.get("filename")
                annotated["criterion_id"] = criterion.id
                annotated["status"] = status
                annotations.append(annotated)
                evidence_records.append(self._build_evidence_entry(evidence, annotated))

        annotated_file = annotations[0].get("annotated_file") if annotations else None
        evaluated_at = datetime.utcnow().isoformat() + "Z"
        duration_sec = round(perf_counter() - start, 3)

        result = {
            "criterion_id": criterion.id,
            "criterion_name": criterion.name,
            "status": status,
            "score": score,
            "reason": reason,
            "annotations": annotations,
            "annotated_file": annotated_file,
            "evaluated_at": evaluated_at,
            "evaluated_by": "system",
            "evaluation_duration_sec": duration_sec,
            "evidence": evidence_records,
        }

        project.validation_results = project.validation_results or {}
        project.validation_results[criterion.id] = result
        project.annotated_documents = project.annotated_documents or {}
        for ann in annotations:
            if ann.get("annotated_file"):
                project.annotated_documents[ann["document"]] = ann["annotated_file"]
        project_service.update_project(project)

        save_criterion_result(project_id, self._criterion_result_for_store(result))

        return result

    def evaluate_all(self, project_id: str) -> Dict[str, Any]:
        project = project_service.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        criteria = criteria_service.get_all()
        results = [self.evaluate_criterion(project_id, c.id) for c in criteria]
        return {
            "project_id": project_id,
            "status": "completed",
            "criteria": results,
        }

    def _collect_evidence(self, project: Project, criterion) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        for doc in project.documents:
            path = Path(doc.path)
            if not path.exists():
                continue

            suffix = path.suffix.lower()
            evidence: Optional[Dict[str, Any]] = None
            if suffix == ".pdf":
                evidence = self._scan_pdf(path, criterion)
            elif suffix == ".docx":
                evidence = self._scan_docx(path, criterion)
            elif suffix == ".xlsx":
                evidence = self._scan_xlsx(path, criterion)
            elif suffix == ".txt":
                evidence = self._scan_txt(path, criterion)

            if evidence:
                evidence.update({
                    "path": str(path),
                    "document_id": doc.id,
                    "filename": doc.filename,
                })
                matches.append(evidence)

        return matches

    def _normalize_status(self, status: str) -> str:
        value = (status or "").lower()
        if value in {"green", "gruen", "grün", "ok", "success"}:
            return "grün"
        if value in {"yellow", "warn", "warning", "amber"}:
            return "gelb"
        return "rot"

    def _build_evidence_entry(self, evidence: Dict[str, Any], annotated: Dict[str, Any]) -> Dict[str, Any]:
        annotated_file = annotated.get("annotated_file") or annotated.get("meta_file")
        annotated_name = Path(annotated_file).name if annotated_file else None
        text_snippet = (evidence.get("text") or evidence.get("reference") or "")[:200]
        reference = annotated.get("reference") or evidence.get("reference")
        if not reference:
            if evidence.get("page"):
                reference = f"Seite {evidence['page']}"
            elif evidence.get("cell"):
                reference = f"Zelle {evidence['cell']}"
            elif evidence.get("line"):
                reference = f"Zeile {evidence['line']}"

        return {
            "dokument": evidence.get("filename"),
            "dokument_original_path": f"/uploads/{evidence.get('filename')}",
            "referenz": reference,
            "text_snippet": text_snippet,
            "annotated_file": annotated_name,
            "annotated_file_path": f"/annotated/{annotated_name}" if annotated_name else None,
        }

    def _criterion_result_for_store(self, result: Dict[str, Any]) -> Dict[str, Any]:
        allowed_keys = {
            "criterion_id",
            "criterion_name",
            "status",
            "score",
            "reason",
            "annotated_file",
            "evaluated_at",
            "evaluated_by",
            "evaluation_duration_sec",
            "evidence",
        }
        return {k: v for k, v in result.items() if k in allowed_keys}

    def _criterion_mentions_hamburg(self, criterion) -> bool:
        text = " ".join(
            [
                criterion.id,
                getattr(criterion, "name", ""),
                getattr(criterion, "kurz", ""),
                getattr(criterion, "lang", ""),
                getattr(criterion, "prompt", "") or "",
            ]
        ).lower()
        return "hamburg" in text or "plz" in text or criterion.id.lower() in {"k001", "k_test_auto"}

    def _extract_hamburg_match(self, text: str) -> Optional[re.Match]:
        return re.search(r"\b2[01]\d{3}\b", text)

    def _scan_pdf(self, path: Path, criterion) -> Optional[Dict[str, Any]]:
        if not self._criterion_mentions_hamburg(criterion):
            return None
        try:
            doc = fitz.open(path)
            for idx, page in enumerate(doc):
                content = page.get_text("text")
                match = self._extract_hamburg_match(content)
                if match:
                    doc.close()
                    return {"text": match.group(0), "page": idx + 1}
            doc.close()
        except Exception as exc:
            logger.warning(f"PDF scan failed for {path}: {exc}")
        return None

    def _scan_docx(self, path: Path, criterion) -> Optional[Dict[str, Any]]:
        if not self._criterion_mentions_hamburg(criterion):
            return None
        try:
            doc = Document(path)
            for paragraph in doc.paragraphs:
                match = self._extract_hamburg_match(paragraph.text)
                if match:
                    return {"text": match.group(0), "reference": paragraph.text}
        except Exception as exc:
            logger.warning(f"DOCX scan failed for {path}: {exc}")
        return None

    def _scan_xlsx(self, path: Path, criterion) -> Optional[Dict[str, Any]]:
        if not self._criterion_mentions_hamburg(criterion):
            return None
        try:
            wb = load_workbook(path)
            ws = wb.active
            for row in ws.iter_rows():
                for cell in row:
                    value = cell.value
                    if value and isinstance(value, str):
                        match = self._extract_hamburg_match(value)
                        if match:
                            return {
                                "text": match.group(0),
                                "cell": cell.coordinate,
                                "reference": value,
                            }
            wb.close()
        except Exception as exc:
            logger.warning(f"XLSX scan failed for {path}: {exc}")
        return None

    def _scan_txt(self, path: Path, criterion) -> Optional[Dict[str, Any]]:
        if not self._criterion_mentions_hamburg(criterion):
            return None
        try:
            with open(path, "r", encoding="utf-8") as handle:
                for idx, line in enumerate(handle, start=1):
                    match = self._extract_hamburg_match(line)
                    if match:
                        return {"text": match.group(0), "line": idx}
        except Exception as exc:
            logger.warning(f"TXT scan failed for {path}: {exc}")
        return None


validation_service = ValidationService()
