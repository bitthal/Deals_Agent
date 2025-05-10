from fastapi import APIRouter, HTTPException, Depends
from typing import List
import asyncpg
from logger_config import logger

from ..dependencies.database import get_db_connection
from ..models.deals import DealSuggestion, DealSuggestionRequest
from ..services.ai_service import get_deal_suggestions

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