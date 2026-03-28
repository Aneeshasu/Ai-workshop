from app.mcp_server.server import mcp
from app.repositories.receipt_repository import ReceiptRepository
from app.schemas.receipt import Receipt


receipt_repository = ReceiptRepository()


@mcp.tool(
    name="save_receipt_data",
    description="Save validated receipt data to the database and return the saved receipt id."
)
def save_receipt_data(receipt: Receipt) -> dict:
    receipt_id = receipt_repository.save_receipt(receipt)

    return {
        "success": True,
        "receipt_id": receipt_id
    }