import httpx
from typing import Dict, Any
from ..models.deals import CreateDealRequest, CreateDealResponse, DealResponseData
from logger_config import logger

class UpswapService:
    BASE_URL = "https://api.upswap.app/api"
    
    @staticmethod
    async def create_deal(deal_data: CreateDealRequest) -> CreateDealResponse:
        """
        Create a deal using the Upswap API
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{UpswapService.BASE_URL}/create-deal/hackathon/",
                    json=deal_data.model_dump(),
                    timeout=30.0
                )
                
                response.raise_for_status()
                api_response = response.json()
                
                # Extract the data from the API response
                if api_response.get('data'):
                    deal_data = api_response['data']
                    return CreateDealResponse(
                        success=True,
                        message=api_response.get('message', 'Deal created successfully'),
                        data=DealResponseData(**deal_data)
                    )
                else:
                    return CreateDealResponse(
                        success=False,
                        message="No deal data received from API",
                        error="Missing deal data in response"
                    )
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while creating deal: {str(e)}")
            return CreateDealResponse(
                success=False,
                message="Failed to create deal",
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error occurred while creating deal: {str(e)}")
            return CreateDealResponse(
                success=False,
                message="Failed to create deal",
                error=str(e)
            ) 