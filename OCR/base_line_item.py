from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str

    quantity_ordered: Optional[float] = Field(
        default=None,
        alias="qty_ordered"
    )
    quantity_shipped: Optional[float] = Field(
        default=None,
        alias="qty_shipped"
    )
    unit_price: Optional[float] = Field(
        default=None,
        alias="price"
    )
    amount: Optional[float] = None

    class Config:
        populate_by_name = True
        extra = "ignore"


class DocumentData(BaseModel):
    name: Optional[str] = Field(
        default=None,
        alias="vendor_name"
    )
    address: Optional[str] = None

    invoice_number: Optional[str] = Field(
        default=None,
        alias="invoice_no"
    )
    po_number: Optional[str] = Field(
        default=None,
        alias="po_no"
    )
    grn_number: Optional[str] = Field(
        default=None,
        alias="grn_no"
    )

    total: Optional[float] = Field(
        default=None,
        alias="total_amount"
    )

    line_items: List[LineItem] = Field(
        default_factory=list
    )

    class Config:
        populate_by_name = True
        extra = "ignore"
