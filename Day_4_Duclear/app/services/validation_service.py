from app.schemas.receipt import Receipt
from app.schemas.validation import ValidationIssue, ValidationResult


class ValidationService:
    """
    Service responsible for validating parsed receipt data.
    """

    def validate_receipt(
        self,
        receipt: Receipt,
        average_confidence: float | None = None ) -> ValidationResult:
        
        warnings: list[ValidationIssue] = []
        errors: list[ValidationIssue] = []

        # Check if merchant is missing
        if not receipt.merchant:
            warnings.append(
                ValidationIssue(
                    field="merchant",
                    message="Merchant name is missing"
                )
            )

        # Check if total is missing
        if receipt.total is None:
            errors.append(
                ValidationIssue(
                    field="total",
                    message="Total amount is missing"
                )
            )

        # Check if no items were extracted
        if not receipt.items:
            errors.append(
                ValidationIssue(
                    field="items",
                    message="No receipt items were extracted"
                )
            )

        # Check OCR confidence
        if average_confidence is not None and average_confidence < 70:
            errors.append(
                ValidationIssue(
                    field="average_confidence",
                    message="OCR confidence is too low"
                )
            )

        # Check if item totals roughly match receipt total
        item_sum = sum(
            item.total_price for item in receipt.items
            if item.total_price is not None
        )

        if receipt.total is not None and receipt.items:
            if abs(item_sum - receipt.total) > 2.0:
                warnings.append(
                    ValidationIssue(
                        field="total",
                        message="Sum of item totals does not closely match receipt total"
                    )
                )

        # Decide recommended action
        if errors:
            if any(issue.field == "average_confidence" for issue in errors):
                recommended_action = "reupload"
            else:
                recommended_action = "manual_review"
            is_valid = False
        else:
            recommended_action = "save"
            is_valid = True

        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            recommended_action=recommended_action
        )