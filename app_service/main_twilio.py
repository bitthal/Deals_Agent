import os
import json # For content_variables and logging
from typing import Optional, Dict, Any
import uvicorn
from fastapi import FastAPI, Request, Form, Response, HTTPException, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, validator as pydantic_validator, root_validator # Renamed import for clarity or ensure no local override
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
# Assuming logger_config.py is set up
from logger_config import logger

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Twilio Configuration ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER") # For SMS
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER") # For WhatsApp

logger.info(f"TWILIO_ACCOUNT_SID loaded: {'Set' if TWILIO_ACCOUNT_SID else 'Not Set'}")
logger.info(f"TWILIO_AUTH_TOKEN loaded  : {'Set' if TWILIO_AUTH_TOKEN else 'Not Set'}")
logger.info(f"TWILIO_PHONE_NUMBER loaded: {'Set' if TWILIO_PHONE_NUMBER else 'Not Set'}")      
logger.info(f"TWILIO_WHATSAPP_NUMBER loaded: {'Set' if TWILIO_WHATSAPP_NUMBER else 'Not Set'}")

# Logging loaded status
logger.debug(f"TWILIO_ACCOUNT_SID loaded: {'Set' if TWILIO_ACCOUNT_SID else 'Not Set'}")
logger.debug(f"TWILIO_AUTH_TOKEN loaded: {'Set' if TWILIO_AUTH_TOKEN else 'Not Set'}")
logger.debug(f"TWILIO_PHONE_NUMBER (for SMS) loaded: {'Set' if TWILIO_PHONE_NUMBER else 'Not Set'}")
logger.debug(f"TWILIO_WHATSAPP_NUMBER (for WhatsApp) loaded: {'Set' if TWILIO_WHATSAPP_NUMBER else 'Not Set'}")

# Initialize Twilio Client (shared for SMS and WhatsApp)
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        logger.info("Twilio Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio Client: {e}")
else:
    logger.warning("TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not found. Twilio client not initialized.")

# Initialize Twilio Request Validator (for webhook, if needed, uses TWILIO_AUTH_TOKEN)
# RENAMED this variable to avoid conflict with pydantic.validator
twilio_request_validator = None
if TWILIO_AUTH_TOKEN:
    try:
        twilio_request_validator = RequestValidator(TWILIO_AUTH_TOKEN)
        logger.info("Twilio RequestValidator initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio RequestValidator: {e}")
else:
    logger.warning("TWILIO_AUTH_TOKEN not found for twilio_request_validator. Webhook signature validation will be SKIPPED.")


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: FastAPI server is starting.")
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.warning("Reminder: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not set. Twilio functionalities will fail.")
    if not TWILIO_PHONE_NUMBER:
        logger.warning("Reminder: TWILIO_PHONE_NUMBER not set. Sending SMS will not be possible.")
    if not TWILIO_WHATSAPP_NUMBER:
        logger.warning("Reminder: TWILIO_WHATSAPP_NUMBER not set. Sending WhatsApp messages will not be possible.")
    #... (rest of your startup logging)


# --- Pydantic Model for WhatsApp Request ---
class WhatsAppMessageRequest(BaseModel):
    to_number: str  # Expecting E.164 format, e.g., +1234567890
    message_body: Optional[str] = None
    content_sid: Optional[str] = None
    content_variables: Optional[Dict[str, Any]] = None
    status_callback_url_override: Optional[str] = None

    @pydantic_validator('to_number') # Use the aliased or direct pydantic validator
    def validate_to_number_format(cls, v):
        if not v.startswith('+'):
            raise ValueError('to_number must be in E.164 format, e.g., +1234567890')
        return v

    @root_validator(skip_on_failure=True) # Prevents running if individual field validation fails
    def check_message_logic(cls, values):
        message_body = values.get('message_body')
        content_sid = values.get('content_sid')
        content_variables = values.get('content_variables')

        if not message_body and not content_sid:
            raise ValueError('Either message_body or content_sid must be provided.')

        if message_body and content_sid:
            logger.warning("Both message_body and content_sid provided. Prioritizing content_sid (template). message_body will be ignored.")
            values['message_body'] = None # Explicitly nullify message_body if template is used

        if content_sid and content_variables is None:
            # This is acceptable if the template has no variables.
            logger.debug("content_sid provided without content_variables. Valid if template has no placeholders.")

        if not content_sid and content_variables:
            raise ValueError('content_variables provided without content_sid. content_variables can only be used with templates.')
        return values

# --- New WhatsApp Sending Endpoint ---
@app.post("/send_whatsapp")
async def send_whatsapp_message(request_data: WhatsAppMessageRequest = Body(...)):
    logger.info("--- New POST request to /send_whatsapp ---")
    logger.debug(f"Request body: {request_data.model_dump_json(indent=2)}")

    if not twilio_client:
        logger.error("Twilio client not initialized. Cannot send WhatsApp message. Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN.")
        raise HTTPException(status_code=503, detail="Twilio client not configured on server.")

    if not TWILIO_WHATSAPP_NUMBER:
        logger.error("TWILIO_WHATSAPP_NUMBER not configured. Cannot send WhatsApp message.")
        raise HTTPException(status_code=503, detail="Sender WhatsApp number (TWILIO_WHATSAPP_NUMBER) not configured on server.")

    # Construct 'from' and 'to' numbers with 'whatsapp:' prefix
    from_whatsapp_number = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
    to_whatsapp_number = f"whatsapp:{request_data.to_number}"

    message_params = {
        "from_": from_whatsapp_number,
        "to": to_whatsapp_number,
    }

    if request_data.content_sid:
        logger.info(f"Preparing to send templated WhatsApp message using ContentSid: {request_data.content_sid}")
        message_params["content_sid"] = request_data.content_sid
        if request_data.content_variables:
            # Convert dict to JSON string for Twilio API
            message_params["content_variables"] = json.dumps(request_data.content_variables)
            logger.debug(f"Using ContentVariables: {message_params['content_variables']}")
        # message_body is intentionally ignored if content_sid is present, as per Pydantic model logic
    elif request_data.message_body: # This will be true only if content_sid was not provided
        logger.info("Preparing to send free-form WhatsApp message.")
        message_params["body"] = request_data.message_body
    else:
        # This case should ideally be caught by Pydantic validation, but as a safeguard:
        logger.error("No message_body or content_sid provided after Pydantic validation. This should not happen.")
        raise HTTPException(status_code=400, detail="Internal error: Message content missing.")


    if request_data.status_callback_url_override:
        message_params["status_callback"] = request_data.status_callback_url_override
        logger.info(f"Using custom status_callback URL: {request_data.status_callback_url_override}")
    else:
        logger.info("Using status_callback URL configured in Twilio Messaging Service (if any for this sender).")

    try:
        logger.debug(f"Calling Twilio API: client.messages.create with params: {json.dumps(message_params, indent=2)}")
        message = twilio_client.messages.create(**message_params)

        logger.info("WhatsApp message request sent successfully to Twilio!")
        logger.debug(f"Twilio message object attributes:")
        logger.debug(f"  SID: {message.sid}")
        logger.debug(f"  Status (initial): {message.status}") # Usually 'queued' or 'sent'
        logger.debug(f"  To: {message.to}")
        logger.debug(f"  From: {message.from_}")
        logger.debug(f"  Price: {message.price} {message.price_unit if message.price else 'N/A'}")
        logger.debug(f"  Error Code (initial): {message.error_code}")
        logger.debug(f"  Error Message (initial): {message.error_message}")

        return JSONResponse(
            content={
                "status": "success",
                "message_sid": message.sid,
                "to": message.to,
                "from": message.from_,
                "message_status_from_twilio_api_call": message.status,
                "details": "Message queued with Twilio. Final status will be sent to callback URL if configured."
            },
            status_code=202 # Accepted for processing
        )
    except TwilioRestException as e:
        logger.error(f"Twilio API error while sending WhatsApp to {to_whatsapp_number}: Code={e.code}, Status={e.status}, Message='{e.msg}', URI='{e.uri}'")
        error_detail = {
            "status": "error",
            "error_type": "twilio_api_error",
            "error_message": e.msg,
            "error_code": e.code,
            "more_info_url": e.uri, # Very important for debugging
            "status_code_from_twilio": e.status
        }
        http_status_code = e.status if isinstance(e.status, int) and 400 <= e.status < 600 else 500

        # WhatsApp specific error interpretations (add more as needed)
        if e.code == 21211: # Invalid 'To' number
            error_detail["detail"] = f"The 'To' WhatsApp number ({request_data.to_number}) is not valid or incorrectly formatted. Ensure it is in E.164 format (e.g., +1234567890) and is a WhatsApp-enabled number."
            http_status_code = 400
        elif e.code == 21608: # Trial account sending to unverified number OR Sandbox user not opted-in
            error_detail["detail"] = "Failed to send. If using a Twilio trial account, the recipient number must be verified in your Twilio console. If using the Twilio Sandbox for WhatsApp, the recipient must first send 'join <your-sandbox-keyword>' to your Sandbox number."
            http_status_code = 400
        elif e.code == 63016: # Template required (freeform message outside 24hr window)
            error_detail["detail"] = "Failed to send freeform message. You are likely outside the 24-hour window for replies. Please use an approved WhatsApp template (ContentSid)."
            http_status_code = 400
        elif e.code == 63003: # Channel could not find To address
            error_detail["detail"] = f"The WhatsApp number ({request_data.to_number}) could not be reached. It might not be a valid WhatsApp account or is currently unreachable."
            http_status_code = 404
        elif e.code == 21705: # From number not a valid WhatsApp sender
            error_detail["detail"] = f"The sender number ({TWILIO_WHATSAPP_NUMBER}) is not a valid WhatsApp sender or is not yet fully provisioned. Check its status in the Twilio console."
            http_status_code = 500 # Server-side configuration issue

        raise HTTPException(status_code=http_status_code, detail=error_detail)
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending WhatsApp to {to_whatsapp_number}: {type(e).__name__} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"status": "error", "error_type": "unexpected_server_error", "message": "An unexpected error occurred on the server."})


# --- (Include other existing endpoints like /, /sms_webhook, /sms_fallback, /sms_status_callback, /send_sms) ---
# --- (Include if __name__ == "__main__": block for uvicorn.run) ---
if __name__ == "__main__":
    module_name = os.path.splitext(os.path.basename(__file__))[0]
    port = int(os.environ.get("PORT", 8008)) # Default to 8008 if not set
    logger.info(f"Starting uvicorn server for application '{module_name}:app' on host 0.0.0.0, port {port}")
    # For development, reload=True is useful. For production, it's often False.
    # Ensure your logger_config.py is set up correctly for uvicorn's logging.
    uvicorn.run(f"{module_name}:app", host="0.0.0.0", port=port, reload=True)
