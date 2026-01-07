
import logging
import time
from pathlib import Path
from docling.document_converter import (
    DocumentConverter,
    InputFormat,
    PdfFormatOption,
)
from docling.datamodel.pipeline_options import (
    ThreadedPdfPipelineOptions,
    OcrAutoOptions,
)
from docling.pipeline.threaded_standard_pdf_pipeline import (
    ThreadedStandardPdfPipeline,
)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_docling")

FILE_PATH = "data/global_knowledge/the-state-of-enterprise-ai_2025-report.pdf"

def test_conversion(do_ocr: bool):
    logger.info(f"--- Testing with do_ocr={do_ocr} ---")
    
    pipeline_options = ThreadedPdfPipelineOptions(
        do_ocr=do_ocr,
        ocr_options=OcrAutoOptions(lang=["deu", "eng"], force_full_page_ocr=False),
        do_table_structure=False,
        generate_page_images=False,
    )
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ThreadedStandardPdfPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )
    
    start = time.time()
    try:
        result = converter.convert(FILE_PATH)
        duration = time.time() - start
        
        pages = getattr(result.document, "pages", {}) if hasattr(result, "document") else {}
        # In Docling v2 result.document.pages is a dict {page_no: Page}
        num_pages = len(pages)
        
        # Count text length
        full_text = ""
        # Access method depends on docling structure, trying standard export
        try:
            full_text = result.document.export_to_markdown()
        except:
             full_text = "Markdown Export Failed"
             
        logger.info(f"Success! Duration: {duration:.2f}s")
        logger.info(f"Pages: {num_pages}")
        logger.info(f"Text Length: {len(full_text)}")
        logger.info(f"Preview: {full_text[:200]}...")
        
    except Exception as e:
        logger.error(f"Failed! Error: {e}")

if __name__ == "__main__":
    path = Path(FILE_PATH)
    size_mb = path.stat().st_size / (1024 * 1024)
    logger.info(f"File: {FILE_PATH} ({size_mb:.2f} MB)")
    
    # 1. Test with OCR DISABLED (Fast)
    test_conversion(do_ocr=False)
    
    # 2. Test with OCR ENABLED (Slow)
    test_conversion(do_ocr=True)
