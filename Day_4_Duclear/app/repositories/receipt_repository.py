from bson import ObjectId
from pymongo import MongoClient

from app.core.config import settings
from app.schemas.receipt import Receipt


class ReceiptRepository:
    """
    Repository responsible for saving and retrieving receipt data from MongoDB.
    """

    def __init__(self) -> None:
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db_name]
        self.collection = self.db["receipts"]

    def save_receipt(self, receipt: Receipt) -> str:
        """
        Save a receipt to MongoDB and return the inserted document id.
        """
        receipt_data = receipt.model_dump()
        result = self.collection.insert_one(receipt_data)
        return str(result.inserted_id)

    def get_receipt_by_id(self, receipt_id: str) -> dict | None:
        """
        Fetch a receipt document by its MongoDB id.
        """
        document = self.collection.find_one({"_id": ObjectId(receipt_id)})

        if not document:
            return None

        document["_id"] = str(document["_id"])
        return document