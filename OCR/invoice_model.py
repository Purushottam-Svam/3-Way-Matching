from typing import List, Optional
from pydantic import BaseModel, Field
from OCR.base_line_item import LineItem


class InvoiceDocument(BaseModel):
    invoice_number: Optional[str] = Field(
        default=None,
        alias="invoice_number"
    )

    date: Optional[str] = Field(default=None, alias="date")

    vendor_name: Optional[str] = Field(
        default=None,
        alias="vendor_name"
    )

    vendor_address: Optional[str] = Field(
        default=None,
        alias="address"
    )

    po_number: Optional[str] = Field(
        default=None,
        alias="po_number"
    )

    total_amount: Optional[float] = Field(
        default=None,
        alias="total"
    )

    line_items: List[LineItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        extra = "ignore"
