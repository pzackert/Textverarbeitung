import time
import logging
import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log Request
        logger.info(f"→ {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log Response
            reason = getattr(response, "reason_phrase", "OK")
            logger.info(f"← {response.status_code} {reason} ({process_time:.3f}s)")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"← 500 Internal Server Error ({process_time:.3f}s) - {str(e)}")
            # DEBUG MODE: Return error to user
            from fastapi.responses import HTMLResponse
            import traceback
            return HTMLResponse(content=f"<h1>Middleware Caught Error</h1><pre>{traceback.format_exc()}</pre>", status_code=500)

from fastapi.responses import JSONResponse
from src.services.system_state import system_state

class StartupBlockingMiddleware(BaseHTTPMiddleware):
    """
    Blocks all API requests (except system endpoints) until system is ready.
    """
    async def dispatch(self, request: Request, call_next):
        # Allow system endpoints, static files, and root (frontend redirect)
        allowed_paths = ["/api/system", "/system", "/static", "/startup", "/favicon.ico", "/docs", "/openapi.json"]
        if any(request.url.path.startswith(p) for p in allowed_paths):
            return await call_next(request)
        
        # Specific Logic for Root: Redirect to startup if not ready
        if request.url.path == "/":
            if system_state.status not in ["ready", "degraded"]:
                 from starlette.responses import RedirectResponse
                 return RedirectResponse(url="/startup")
            return await call_next(request)

        # Do not block test runs
        if os.getenv("PYTEST_CURRENT_TEST"):
            return await call_next(request)

        # Allow if system is ready or degraded (partial functionality)
        if system_state.status in ["ready", "degraded"]:
             return await call_next(request)

        # Otherwise block with 503
        return JSONResponse(
            status_code=503,
            content={
                "error": "System initializing",
                "message": "The system is currently starting up. Please wait.",
                "status": system_state.status,
                "progress": system_state.current_action
            }
        )
