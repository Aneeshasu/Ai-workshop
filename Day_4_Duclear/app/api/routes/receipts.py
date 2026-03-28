import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agent.receipt_agent import ReceiptAgent


router = APIRouter(prefix="/receipts", tags=["receipts"])


UPLOAD_DIR = Path("tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/process")
async def process_receipt(file: UploadFile = File(...)):
    """
    Accept a receipt image, save it temporarily, invoke the Strands agent,
    and return the final response.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_extension = Path(file.filename).suffix if file.filename else ".jpg"
    temp_file_name = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = UPLOAD_DIR / temp_file_name

    try:
        with open(temp_file_path, "wb") as f:
            f.write(file_bytes)

        receipt_agent_builder = ReceiptAgent()
        

        prompt = f"""
            You are processing one uploaded grocery receipt image.

            The local file path of the uploaded receipt image is:
            {temp_file_path}

            Your task:
            1. Use the extract_receipt_text tool with this file path.
            2. Read the OCR output carefully.
            3. Normalize the OCR result into this exact receipt structure:
            - merchant
            - date
            - time
            - currency
            - items
            - discounts
            - subtotal
            - tax
            - total
            - raw_text
            4. Use the validate_receipt_data tool with the parsed receipt and OCR average confidence.
            5. If validation recommends saving, call save_receipt_data.
            6. If validation recommends manual review or reupload, do not save.
            7. Return the final structured result clearly.

            Important rules:
            - Do not invent values unless strongly supported by OCR text.
            - If a field is unclear, use null.
            - Ignore footer/promotional noise when possible.
            - Keep item extraction accurate.
            """

        response = await receipt_agent_builder.invoke(prompt)

        return {
            "success": True,
            "response": str(response),
            "file_path": str(temp_file_path),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process receipt: {str(e)}")

    finally:
        if temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except OSError:
                pass