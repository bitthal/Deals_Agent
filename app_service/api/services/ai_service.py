import os
import json
import re
from typing import Dict, Any, List
import google.generativeai as genai
from logger_config import logger
from ..models.deals import EventData, InventoryItem, DealSuggestion, DealSuggestionRequest
from config.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME
import asyncpg

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL_NAME)

def generate_deal_from_ai(event_data: EventData, inventory_list: List[InventoryItem]) -> Dict[str, Any]:
    """Generates a product deal suggestion using a generative AI model."""
    if not GEMINI_API_KEY:
        logger.error("AI API Key is not configured.")
        raise ValueError("AI API Key not configured.")

    try:
        generation_config = {
            "temperature": 0.7, "top_p": 0.95, "top_k": 40,
            "max_output_tokens": 1024, "response_mime_type": "application/json",
        }
        safety_settings = [
            {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                      "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
        ]
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        prompt = f"""
        You are an expert marketing assistant. Analyze event details and inventory to suggest ONE compelling product deal.
        Event: {json.dumps(event_data.model_dump(), indent=2)}
        Inventory: {json.dumps([item.model_dump() for item in inventory_list], indent=2)}

        Select ONE product. Discount should be 10-30% or a meaningful fixed amount.
        'deal_details_suggestion_text' should be catchy, concise, highlight benefit/savings, and relevant to the event.
        'suggested_product_sku' must be from inventory. Use its 'price' as 'original_price'.
        Calculate 'suggested_price'. 'suggested_discount_type' is 'fixed_amount' or 'percentage'.
        If 'percentage', 'suggested_discount_value' is the percent number (e.g., 20 for 20%).
        If 'fixed_amount', 'suggested_discount_value' is currency amount (e.g., 80.00).

        Respond ONLY with a single JSON object:
        {{
          "suggested_product_sku": "string",
          "deal_details_suggestion_text": "string",
          "suggested_discount_type": "string",
          "suggested_discount_value": "float",
          "original_price": "float",
          "suggested_price": "float"
        }}
        Example for a marathon and umbrella:
        {{
          "suggested_product_sku": "UMB-LG-BLK-001",
          "deal_details_suggestion_text": "Beat the rain at the {event_data.event_name}! Large Umbrella, was ₹400, now ₹320! Stay dry. Limited stock!",
          "suggested_discount_type": "fixed_amount",
          "suggested_discount_value": 80.00,
          "original_price": 400.00,
          "suggested_price": 320.00
        }}
        """
        response = model.generate_content(prompt)

        if not response.parts:
            block_reason = "Unknown reason."
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason_message or str(response.prompt_feedback.block_reason)
            logger.error(f"AI model did not return content. Blocked: {block_reason}")
            raise ValueError(f"AI model response empty/blocked: {block_reason}")

        ai_output_json = response.text
        match = re.search(r"```json\s*([\s\S]*?)\s*```", ai_output_json, re.DOTALL)
        if match:
            ai_output_json = match.group(1)
        
        deal_suggestion = json.loads(ai_output_json)

        # Validation
        selected_sku = deal_suggestion.get("suggested_product_sku")
        inventory_map = {item.sku: item for item in inventory_list}

        if not selected_sku or selected_sku not in inventory_map:
            logger.error(f"AI suggested SKU '{selected_sku}' not in inventory.")
            raise ValueError(f"AI suggested SKU '{selected_sku}' not in inventory.")
        
        actual_item = inventory_map[selected_sku]
        deal_suggestion["original_price"] = actual_item.price # Enforce actual price

        original_price = deal_suggestion["original_price"]
        discount_type = deal_suggestion.get("suggested_discount_type")
        discount_value = float(deal_suggestion.get("suggested_discount_value", 0))
        
        calculated_suggested_price = original_price
        if discount_type == "fixed_amount":
            calculated_suggested_price = original_price - discount_value
        elif discount_type == "percentage":
            calculated_suggested_price = original_price * (1 - discount_value / 100)
        
        # Use calculated price, rounded, and warn if AI's differs significantly
        if abs(deal_suggestion.get("suggested_price", float('inf')) - calculated_suggested_price) > 0.01:
            logger.warning(
                f"AI suggested price {deal_suggestion.get('suggested_price')} differs from "
                f"calculated {calculated_suggested_price:.2f} for SKU {selected_sku}. Using calculated."
            )
        deal_suggestion["suggested_price"] = round(calculated_suggested_price, 2)

        return deal_suggestion

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI JSON response: {e}. Raw: {response.text if 'response' in locals() else 'N/A'}", exc_info=True)
        raise ValueError(f"AI response not valid JSON: {e}")
    except genai.types.generation_types.BlockedPromptException as e:
        logger.error(f"AI prompt blocked: {e}", exc_info=True)
        raise # Re-raise to be caught by endpoint
    except Exception as e:
        logger.error(f"Unexpected AI interaction error: {e}", exc_info=True)
        raise ValueError(f"Unexpected error during AI interaction: {str(e)}")

async def get_deal_suggestions(
    request: DealSuggestionRequest,
    conn: asyncpg.Connection
) -> List[DealSuggestion]:
    """
    Generate deal suggestions using AI based on event details and inventory.
    """
    try:
        # Prepare context for AI
        context = f"""
        Event Details:
        - Name: {request.event_details.event_name}
        - Type: {request.event_details.event_type}
        - Date: {request.event_details.event_date}
        - Target Audience: {request.event_details.target_audience or 'Not specified'}
        - Special Requirements: {request.event_details.special_requirements or 'None'}

        Available Inventory:
        {format_inventory(request.inventory_list)}
        """

        # Generate suggestions using AI
        response = await model.generate_content_async(
            f"""Based on the following event and inventory information, suggest appropriate deals:
            {context}
            
            Provide suggestions in the following format:
            - Product SKU
            - Suggested discount percentage
            - Reasoning for the suggestion
            - Estimated impact
            - Alternative suggestions (if any)
            """
        )

        # Parse AI response and create suggestions
        suggestions = parse_ai_response(response.text, request.inventory_list)
        return suggestions

    except Exception as e:
        logger.error(f"Error generating deal suggestions: {str(e)}")
        raise

def format_inventory(inventory_list: List[dict]) -> str:
    """Format inventory list for AI context."""
    return "\n".join([
        f"- {item.sku}: {item.name} ({item.category}) - ${item.current_price} - {item.quantity_available} available"
        for item in inventory_list
    ])

def parse_ai_response(response: str, inventory_list: List[dict]) -> List[DealSuggestion]:
    """Parse AI response into structured suggestions."""
    suggestions = []
    current_suggestion = {}
    
    for line in response.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('- Product SKU:'):
            if current_suggestion:
                suggestions.append(DealSuggestion(**current_suggestion))
            current_suggestion = {'suggested_product_sku': line.split(':', 1)[1].strip()}
        elif line.startswith('- Suggested discount:'):
            current_suggestion['suggested_discount'] = float(line.split(':', 1)[1].strip().rstrip('%'))
        elif line.startswith('- Reasoning:'):
            current_suggestion['reasoning'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Estimated impact:'):
            current_suggestion['estimated_impact'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Alternative suggestions:'):
            current_suggestion['alternative_suggestions'] = [
                alt.strip() for alt in line.split(':', 1)[1].strip().split(',')
            ]
    
    if current_suggestion:
        suggestions.append(DealSuggestion(**current_suggestion))
    
    return suggestions 