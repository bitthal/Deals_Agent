from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, conlist
from datetime import datetime

class EventDetails(BaseModel):
    event_name: str
    event_date: datetime
    event_type: str
    target_audience: Optional[str] = None
    special_requirements: Optional[str] = None

class InventoryItem(BaseModel):
    sku: str
    name: str
    category: str
    current_price: float
    quantity_available: int
    description: Optional[str] = None

class DealSuggestionRequest(BaseModel):
    event_details: EventDetails
    inventory_list: List[InventoryItem]

class DealSuggestion(BaseModel):
    suggested_product_sku: str
    suggested_discount: float
    reasoning: str
    estimated_impact: Optional[str] = None
    alternative_suggestions: Optional[List[str]] = None

class DealSuggestionResponse(BaseModel):
    suggested_product_sku: str
    deal_details_suggestion_text: str
    suggested_discount_type: str  # "fixed_amount" or "percentage"
    suggested_discount_value: float
    original_price: float
    suggested_price: float
    message: str = Field(default="Deal suggestion generated successfully.")

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Union[str, List[str]]] = None 