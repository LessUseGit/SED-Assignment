from fastapi import Request


def add_flash_message(request: Request, message: str, category: str = "info"):
    """
    Adds a flash message to the session for displaying temporary notifications.

    Args:
        request (Request): The incoming request object.
        message (str): The message content.
        category (str, optional): The category of the message (e.g., 'info', 'warning'). Defaults to "info".
    """
    flash_message = {"message": message, "category": category}
    request.session.setdefault("flash", []).append(flash_message)


def get_flash_messages(request: Request):
    """
    Retrieves flash messages stored in the session.

    Args:
        request (Request): The incoming request object.

    Returns:
        list: A list of flash messages.
    """
    messages = request.session.pop("flash", [])
    return messages
