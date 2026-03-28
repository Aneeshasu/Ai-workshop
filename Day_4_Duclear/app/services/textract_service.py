import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.schemas.textract import TextractLine, TextractResult


class TextractService:
    """
    Service responsible for calling AWS Textract and converting
    the raw response into our internal TextractResult schema.
    """

    def __init__(self) -> None:
        self.client = boto3.client(
            "textract",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def extract_text_from_file(self, file_path: str) -> TextractResult:
        """
        Read an image file from disk and extract text using Textract.
        """
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        return self.extract_text_from_bytes(image_bytes)

    def extract_text_from_bytes(self, image_bytes: bytes) -> TextractResult:
        """
        Sends image bytes to AWS Textract DetectDocumentText
        and returns a simplified TextractResult.
        """
        try:
            response = self.client.detect_document_text(
                Document={"Bytes": image_bytes}
            )
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to call Textract: {str(e)}") from e

        lines = []
        confidence_values = []

        for block in response.get("Blocks", []):
            if block.get("BlockType") == "LINE":
                text = block.get("Text", "").strip()
                confidence = block.get("Confidence")

                if text:
                    lines.append(
                        TextractLine(
                            text=text,
                            confidence=confidence
                        )
                    )

                if confidence is not None:
                    confidence_values.append(confidence)

        raw_text = "\n".join(line.text for line in lines) if lines else None
        average_confidence = (
            sum(confidence_values) / len(confidence_values)
            if confidence_values
            else None
        )

        return TextractResult(
            lines=lines,
            raw_text=raw_text,
            average_confidence=average_confidence
        )