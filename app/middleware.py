from fastapi import Request


def add_flash_message(request: Request, message: str, category: str = "info"):
    flash_message = {"message": message, "category": category}
    request.session.setdefault("flash", []).append(flash_message)


def get_flash_messages(request: Request):
    messages = request.session.pop("flash", [])
    return messages
