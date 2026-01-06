from starlette.types import ASGIApp, Message, Receive, Scope, Send


class FixContentTypeMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and scope["method"] in ("POST", "PUT", "PATCH"):
            headers = dict(scope["headers"])
            if b"content-type" not in headers:
                # Find the content-type from the message if it's not in the scope
                async def receive_wrapper() -> Message:
                    message = await receive()
                    if message["type"] == "http.request":
                        if "headers" in message:
                            headers_dict = dict(message["headers"])
                            if b"content-type" in headers_dict:
                                scope["headers"].append(
                                    (b"content-type", headers_dict[b"content-type"])
                                )
                    return message

                await self.app(scope, receive_wrapper, send)
                return
        await self.app(scope, receive, send)
