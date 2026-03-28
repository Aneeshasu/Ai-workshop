from app.mcp_server.server import mcp
from app.schemas.textract import TextractResult
from app.services.textract_service import TextractService


textract_service = TextractService()


@mcp.tool(
    name="extract_receipt_text",
    description="Extract text from a receipt image file using AWS Textract and return simplified OCR output."
)
def extract_receipt_text(file_path: str) -> TextractResult:
    return textract_service.extract_text_from_file(file_path)