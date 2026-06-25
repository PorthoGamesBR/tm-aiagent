from fastapi import Depends, Request

from bootstrap import Application


def get_application(request: Request) -> Application:
    return request.app.state.application


def get_chat_service(
    application: Application = Depends(get_application)
):
    return application.chat_service