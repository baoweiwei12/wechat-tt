from functools import wraps
from typing import Any, Callable, TypedDict
from fastapi import Body
import requests


class WcfError(Exception):
    def __init__(self, message: str | None) -> None:
        self.message = f"WcfError: {message}" if message else "WcfError: unknown error"

    def __str__(self):
        return self.message


class WcfResponse(TypedDict):
    data: Any
    error: str | None
    status: int


class UserInfo(TypedDict):
    wxid: str
    name: str
    mobile: str
    home: str
    small_head_url: str
    big_head_url: str


class WcfClient:
    def __init__(self, api_base: str):
        self.api_base = api_base
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.api_base}{path}"
    def _handle_response(self, response: requests.Response):
        try:
            response.raise_for_status()
            json_data: WcfResponse = response.json()
            if json_data["status"] != 0:
                raise WcfError(json_data["error"])
            return json_data
        except requests.exceptions.RequestException as e:
            raise WcfError(str(e))
        except Exception as e:
            raise WcfError(str(e))

    def send_text(self,msg: str,receiver: str,aters: str="",):
        json_data = {
        "aters":aters,
        "msg": msg,
        "receiver": receiver
        }
        resp = self.session.post(self._url("/text"),json=json_data)
        self._handle_response(resp)

    def get_userinfo(self):
        resp = self.session.get(self._url("/userinfo"))
        data = self._handle_response(resp)
        return UserInfo(data["data"])
        