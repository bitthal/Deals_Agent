from fastapi import APIRouter, HTTPException, Depends
from typing import List
import asyncpg
from logger_config import logger

from ..dependencies.database import get_db_connection
from ..models.deals import DealSuggestion, DealSuggestionRequest, ErrorResponse, CreateDealRequest, CreateDealResponse
from ..services.ai_service import get_deal_suggestions
from ..services.upswap_service import UpswapService

router = APIRouter(
    prefix="/deals",
    tags=["deals"],
    responses={404: {"description": "Not found"}},
)

@router.post("/suggest", response_model=List[DealSuggestion])
async def suggest_deals(
    request: DealSuggestionRequest,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Get AI-powered deal suggestions based on the provided criteria.
    """
    try:
        # Get deal suggestions from AI service
        suggestions = await get_deal_suggestions(request, conn)
        return suggestions
    except Exception as e:
        logger.error(f"Error getting deal suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get deal suggestions")

@router.post("/create-deal", response_model=CreateDealResponse)
async def create_deal(deal_data: CreateDealRequest):
    """
    Create a new deal using the Upswap API
    """
    try:
        response = await UpswapService.create_deal(deal_data)
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail=response.error or "Failed to create deal"
            )
        return response
    except Exception as e:
        logger.error(f"Error in create_deal endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 