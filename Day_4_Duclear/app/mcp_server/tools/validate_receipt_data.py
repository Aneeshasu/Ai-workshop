from app.mcp_server.server import mcp
from app.schemas.receipt import Receipt
from app.schemas.validation import ValidationResult
from app.services.validation_service import ValidationService


validation_service = ValidationService()


@mcp.tool(
    name="validate_receipt_data",
    description="Validate parsed receipt data and return warnings, errors, and the recommended next action."
)
def validate_receipt_data(
    receipt: Receipt,
    average_confidence: float | None = None) -> ValidationResult:
    return validation_service.validate_receipt(
        receipt=receipt,
        average_confidence=average_confidence
    )