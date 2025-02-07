from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from jose.exceptions import ExpiredSignatureError

from app.main import app
from app.middleware import add_flash_message


@app.exception_handler(ExpiredSignatureError)
def expired_token_handler(request: Request):
    add_flash_message(
        request, "Session expired. Please log in again.", category="warning"
    )
    return RedirectResponse(url="/login")


@app.exception_handler(HTTPException)
def auth_exception_handler(request: Request, exc: HTTPException):
    print("here")
    if exc.status_code == 401:
        add_flash_message(
            request, "Invalid user token, please login again", category="danger"
        )
        return RedirectResponse(url="/login")
    # return await request.app.default_exception_handler(request, exc)
