import json
from abc import abstractmethod
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import BaseServer
from typing import Callable, cast

from meeting_info import MeetingInfo


class Callbacks:

    @abstractmethod
    def meeting(self, info: MeetingInfo):
        pass

    @abstractmethod
    def free(self, message: str):
        pass


class CallAdapter:

    @property
    @abstractmethod
    def path(self):
        pass

    @abstractmethod
    def handle(self, data: bytes) -> bool:
        pass


class MeetingCallAdapter(CallAdapter):

    def __init__(self, callback: Callable[[MeetingInfo], None]):
        self.callback = callback

    @property
    def path(self):
        return "/meeting"

    def handle(self, data: bytes) -> bool:
        try:
            meeting_info_raw = cast(dict, json.loads(data))
            title = meeting_info_raw.get("title")
            time_info = meeting_info_raw.get("time_info")
            time_token = meeting_info_raw.get("time_token")
            is_free = meeting_info_raw.get("is_free")
            if title is not None and time_info is not None and time_token is not None and is_free is not None:
                self.callback(
                    MeetingInfo(
                        title=title,
                        time_info=time_info,
                        time_token=time_token,
                        is_free=is_free
                    )
                )
                return True
            return False
        except Exception as e:
            print(e)
            return False


class FreeCallAdapter(CallAdapter):

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    @property
    def path(self):
        return "/free"

    def handle(self, data: bytes) -> bool:
        free_info_raw = cast(dict, json.loads(data))
        message = free_info_raw.get("message")
        if message is not None:
            self.callback(message)
            return True
        return False


class CommandServer:

    def __init__(self, address: tuple[str, int], callbacks: Callbacks):
        self.address = address
        self.adapters = [
            MeetingCallAdapter(callback=callbacks.meeting),
            FreeCallAdapter(callback=callbacks.free)
        ]

    def start(self):
        server = CallbackServer(
            server_address=self.address,
            adapters=self.adapters,
            RequestHandlerClass=ScreenCommandHandler,
        )
        server.serve_forever()


class CallbackServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int], adapters: list[CallAdapter], RequestHandlerClass):
        self.adaptersMap = dict(map(lambda adapter: (cast(CallAdapter, adapter).path, adapter), adapters))
        super().__init__(server_address, RequestHandlerClass)


class ScreenCommandHandler(BaseHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: tuple[str, int], server: BaseServer):
        super().__init__(request, client_address, server)

    def do_POST(self):
        adapter = cast(CallAdapter, cast(CallbackServer, self.server).adaptersMap.get(self.path))
        if adapter is not None:
            content_length = int(self.headers.get("Content-Length"))
            data = self.rfile.read(content_length)
            handled = adapter.handle(data=data)
            if handled:
                self.send_response(HTTPStatus.OK)
            else:
                self.send_response(HTTPStatus.BAD_REQUEST)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def display_handler(self):
        self.send_response(HTTPStatus.OK)
