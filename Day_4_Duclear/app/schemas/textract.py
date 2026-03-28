from typing import List, Optional
from pydantic import BaseModel, Field


class TextractLine(BaseModel):
    """
    Represents one detected line of text from Textract.
    Example: 'MILK 3.49'
    """

    text: str = Field(..., description="Detected text line")
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for this line"
    )


class TextractResult(BaseModel):
    """
    Simplified OCR result from Textract that our app will use.
    """

    lines: List[TextractLine] = Field(
        default_factory=list,
        description="List of detected text lines"
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="All detected lines joined into one text block"
    )
    average_confidence: Optional[float] = Field(
        default=None,
        description="Average OCR confidence across detected lines"
    )