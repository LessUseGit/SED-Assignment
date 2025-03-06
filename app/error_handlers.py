from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from jose.exceptions import ExpiredSignatureError
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from app.middleware import add_flash_message


def expired_token_handler(request: Request, exc: ExpiredSignatureError):
    """
    Handles expired token errors by redirecting the user to the login page.

    Args:
        request (Request): The incoming request object.
        exc (ExpiredSignatureError): The expired token exception.

    Returns:
        RedirectResponse: Redirects the user to the login page with a session expiration message.
    """
    add_flash_message(
        request, "Session expired. Please log in again.", category="warning"
    )
    return RedirectResponse(url="/login")


def auth_exception_handler(request: Request, exc: HTTPException):
    """
    Handles authentication exceptions by redirecting the user to the login page.

    Args:
        request (Request): The incoming request object.
        exc (HTTPException): The authentication exception.

    Returns:
        RedirectResponse: Redirects the user to the login page with an error message.
    """
    if exc.status_code == 401:
        add_flash_message(
            request, "Invalid user token, please login again", category="danger"
        )
        return RedirectResponse(url="/login")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )
