"""
Compatibility shim: keep historical import path but delegate to the new
annotation_service implementation. Remove this once downstream imports are
updated everywhere.
"""

from src.services.annotation_service import AnnotationService, annotation_service

PDFAnnotationService = AnnotationService
pdf_annotation_service = annotation_service
