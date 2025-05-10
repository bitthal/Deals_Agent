import os
import uvicorn
from logger_config import logger

if __name__ == "__main__":
    # Determine the module name for uvicorn
    module_name = "api.main"
    
    server_port_str = os.environ.get("PORT", "8008")
    try:
        server_port = int(server_port_str)
    except ValueError:
        logger.warning(f"Invalid SERVER_PORT: '{server_port_str}'. Defaulting to 8008.")
        server_port = 8008

    logger.info(f"Starting Uvicorn server for '{module_name}:app' on 0.0.0.0:{server_port}")
    uvicorn.run(f"{module_name}:app", host="0.0.0.0", port=server_port, reload=True) 