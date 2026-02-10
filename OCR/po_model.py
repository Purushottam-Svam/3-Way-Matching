from typing import List, Optional
from pydantic import BaseModel, Field
from OCR.base_line_item import LineItem


class PurchaseOrderDocument(BaseModel):
    po_number: Optional[str] = Field(
        default=None,
        alias="po_number"
    )

    date: Optional[str] = Field(default=None, alias="date")

    vendor_name: Optional[str] = Field(default=None, alias="vendor_name")
    vendor_address: Optional[str] = Field(default=None, alias="address")

    total_amount: Optional[float] = Field(
        default=None,
        alias="total_amount"
    )

    line_items: List[LineItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        extra = "ignore"
