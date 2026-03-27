from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# --- 1. The Classifier Enum ---
class DocumentCategory(str, Enum):
    PURCHASE_ORDER = "PURCHASE_ORDER"
    BILL_OF_MATERIALS = "BILL_OF_MATERIALS"
    SHIPPING_MANIFEST = "SHIPPING_MANIFEST"
    UNKNOWN = "UNKNOWN"

# --- 2. Shared/Common Models ---
class LineItem(BaseModel):
    description: str = Field(description="Description of the item, part, or service")
    quantity: float = Field(description="Number of units")
    unit_price: Optional[float] = Field(default=None, description="Price per unit, if applicable")
    total_price: Optional[float] = Field(default=None, description="Total price, if applicable")

# --- 3. Specific Document Schemas ---
class PurchaseOrder(BaseModel):
    po_number: str
    vendor_name: str
    date: str
    grand_total: float
    line_items: List[LineItem]
    confidence_score: float = Field(description="Score between 0.0 and 1.0")

class BillOfMaterials(BaseModel):
    project_name: str = Field(description="Name of the engineering project")
    assembly_id: str = Field(description="ID of the master assembly")
    parts_list: List[LineItem] = Field(description="List of required physical parts")
    compliance_check: bool = Field(description="Whether the BOM meets safety standards")
    confidence_score: float

class ShippingManifest(BaseModel):
    tracking_number: str
    carrier: str
    destination_address: str
    weight_lbs: float
    items_shipped: List[LineItem]
    confidence_score: float

# --- 4. The Unified Wrapper (From your outline) ---
class UnifiedExtraction(BaseModel):
    document_type: DocumentCategory = Field(description="The classified type of the document")
    extracted_data: dict = Field(description="The dynamically mapped schema data (PO, BOM, or Manifest)")
