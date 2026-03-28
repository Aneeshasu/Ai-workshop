from typing import List, Literal
from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """
    Represents one warning or error found during validation.
    Example: total mismatch, missing merchant, low OCR confidence
    """

    field: str = Field(..., description="Field related to the issue")
    message: str = Field(..., description="Human-readable description of the issue")


class ValidationResult(BaseModel):
    """
    Represents the final result of validating a parsed receipt.
    """

    is_valid: bool = Field(..., description="Whether the receipt passed validation")
    warnings: List[ValidationIssue] = Field(
        default_factory=list,
        description="Non-blocking validation warnings"
    )
    errors: List[ValidationIssue] = Field(
        default_factory=list,
        description="Blocking validation errors"
    )
    recommended_action: Literal["save", "manual_review", "reupload"] = Field(
        ...,
        description="What the system should do next"
    )