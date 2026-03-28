from typing import Optional, List
from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    """
    Represents one purchased item in the receipt.
    Example: Milk, Bread, Eggs
    """

    name: str = Field(..., description="Name of the purchased item")
    quantity: Optional[str] = Field(
        default=None,
        description="Quantity of the item if available, e.g. '2', '1.5 lb', '3 x'"
    )
    unit_price: Optional[float] = Field(
        default=None,
        description="Price per single unit if available"
    )
    total_price: Optional[float] = Field(
        default=None,
        description="Total price for this item line"
    )


class ReceiptDiscount(BaseModel):
    """
    Represents a discount/coupon line in the receipt.
    Example: Store coupon, loyalty discount
    """

    name: str = Field(..., description="Name of the discount")
    amount: float = Field(..., description="Discount amount")


class Receipt(BaseModel):
    """
    Final normalized receipt structure.
    This is the main schema your system will try to produce.
    """

    merchant: Optional[str] = Field(
        default=None,
        description="Store or merchant name"
    )
    date: Optional[str] = Field(
        default=None,
        description="Receipt date if available, e.g. '2026-03-27'"
    )
    time: Optional[str] = Field(
        default=None,
        description="Receipt time if available, e.g. '14:32:10'"
    )
    currency: Optional[str] = Field(
        default="USD",
        description="Currency used in the receipt"
    )

    items: List[ReceiptItem] = Field(
        default_factory=list,
        description="List of purchased items"
    )
    discounts: List[ReceiptDiscount] = Field(
        default_factory=list,
        description="List of discounts applied on the receipt"
    )

    subtotal: Optional[float] = Field(
        default=None,
        description="Subtotal before tax and final total"
    )
    tax: Optional[float] = Field(
        default=None,
        description="Tax amount"
    )
    total: Optional[float] = Field(
        default=None,
        description="Final total amount paid"
    )

    raw_text: Optional[str] = Field(
        default=None,
        description="Raw OCR text from the receipt for debugging/reference"
    )