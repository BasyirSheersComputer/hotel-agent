"""
Structured Logging Middleware.
Intercepts requests to log start/finish events with duration and context.
"""
import time
import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger()

class StructLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # Bind org_id/user_id if available (after auth middleware runs)
        # Note: Middleware order matters! Auth should run before this if we want user_id in start log,
        # but often logging is outermost. We will check state in the 'finish' log.

        start_time = time.time()
        
        # Log Request Start
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            user_agent=request.headers.get("user-agent"),
        )

        try:
            response = await call_next(request)
            
            # Extract status code
            status_code = response.status_code
            
        except Exception as e:
            # Log Exception
            process_time = time.time() - start_time
            logger.error(
                "request_failed",
                error=str(e),
                duration=process_time,
                method=request.method,
                path=request.url.path,
            )
            raise e

        # Log Request Finish
        process_time = time.time() - start_time
        
        # Add context from request state (set by Auth/Tenant middleware)
        org_id = getattr(request.state, "org_id", None)
        user_id = getattr(request.state, "user_id", None)
        
        logger.info(
            "request_finished",
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration=process_time,
            org_id=org_id,
            user_id=user_id,
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
