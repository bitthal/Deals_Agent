from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, conlist
from datetime import datetime

class EventData(BaseModel):
    vendor_id: str
    location_uuid: str
    event_trigger_point: str
    event_details_text: Dict[str, Any]
    event_location_latitude: float
    event_location_longitude: float
    event_timestamp: datetime

class InventoryItem(BaseModel):
    sku: str
    product_name: str
    description: Optional[str] = None
    price: float
    quantity_on_hand: int
    category: str
    supplier: Optional[str] = None

class DealSuggestion(BaseModel):
    vendor_id: str
    event_id: int
    inventory_item_id: int
    suggested_product_sku: str
    deal_details_prompt: str
    deal_details_suggestion_text: str
    suggested_discount_type: str
    suggested_discount_value: float
    original_price: float
    suggested_price: float
    ai_model_name: str
    ai_response_payload: Dict[str, Any]
    vendor_feedback: str = "pending"
    status: str = "generated"

class DealSuggestionRequest(BaseModel):
    event_data: EventData
    inventory_items: List[InventoryItem]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Union[str, List[str]]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class DealImage(BaseModel):
    thumbnail: str
    compressed: str

class CreateDealRequest(BaseModel):
    deal_title: str
    deal_description: str
    select_service: str
    uploaded_images: List[DealImage]
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    start_now: str
    actual_price: str
    deal_price: str
    available_deals: str
    location_house_no: str
    location_road_name: str
    location_country: str
    location_state: str
    location_city: str
    location_pincode: str
    vendor_kyc: str
    latitude: float
    longitude: float

class DealResponseData(BaseModel):
    deal_uuid: str
    deal_title: str
    deal_description: str
    select_service: str
    uploaded_images: List[DealImage]
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    start_now: bool
    buy_now: bool
    actual_price: str
    deal_price: str
    available_deals: int
    location_house_no: str
    location_road_name: str
    location_country: str
    location_state: str
    location_city: str
    location_pincode: str
    vendor_kyc: str
    vendor_name: str
    vendor_uuid: str
    vendor_email: str
    vendor_number: str
    discount_percentage: float
    latitude: str
    longitude: str
    deal_post_time: str

class CreateDealResponse(BaseModel):
    success: bool
    message: str
    data: Optional[DealResponseData] = None
    error: Optional[str] = None 