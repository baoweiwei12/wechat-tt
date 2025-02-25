import requests
from typing import Any, TypedDict
from pydantic import BaseModel
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GingAIResponseBase(TypedDict):
    """
    通用的GingAI响应基类。
    包含响应数据、状态码和消息。
    """

    data: Any
    code: int
    message: str


class ChatInfo(TypedDict):
    """
    聊天信息类。
    包含聊天ID、消息ID、操作状态、消息内容和是否结束标志。
    """

    chat_id: str
    id: str
    operate: bool
    content: str
    is_end: bool


class GingAIChatResponse(TypedDict):
    """
    聊天响应类，继承自GingAIResponseBase。
    数据字段为ChatInfo类型。
    """

    data: ChatInfo


class GingAIError(Exception):
    """
    自定义GingAI错误类。
    当与GingAI API交互出现错误时抛出。
    """

    def __init__(self, message: str):
        self.message = f"GingAIError: {message}"

    def __str__(self):
        return self.message


class GingAIOptions(BaseModel):
    api_base: str
    api_key: str
    application_id: str


class GingAIClient:
    """
    GingAI客户端类，用于与GingAI API进行交互。
    """

    def __init__(self, api_base: str, api_key: str, application_id: str):
        """
        初始化GingAIClient。

        参数:
        api_base (str): API的基础URL。
        api_key (str): 用于身份验证的API密钥。
        application_id (str): 应用程序的ID。
        """
        self.api_base = api_base
        self.api_key = api_key
        self.application_id = application_id
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"AUTHORIZATION": f"{self.api_key}"})

        # 配置请求重试机制
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _handle_response(self, response: requests.Response) -> GingAIResponseBase:
        """
        处理请求响应，检查状态码和响应内容。

        参数:
        response (requests.Response): 请求的响应对象。

        返回:
        dict: 响应的JSON数据。

        抛出:
        GingAIError: 如果请求失败或返回非预期结果。
        """
        try:
            response.raise_for_status()
            json_data = response.json()
            if json_data.get("code") != 200:
                raise GingAIError(json_data.get("message", "Unknown error"))
            return GingAIResponseBase(**json_data)
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise GingAIError(f"Request failed: {e}")
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise GingAIError(f"Invalid JSON response: {e}")

    def get_chat_id(self) -> str:
        """
        获取聊天ID。

        返回:
        str: 聊天ID。

        抛出:
        GingAIError: 如果请求失败或返回非预期结果。
        """
        url = f"{self.api_base}/application/{self.application_id}/chat/open"
        logger.info(f"Sending request to {url}")
        response = self.session.get(url)
        ging_resp = self._handle_response(response)
        return ging_resp["data"]

    def chat(self, chat_id: str, message: str, re_chat: bool = False):
        """
        发送聊天消息并获取响应。

        参数:
        chat_id (str): 聊天ID。
        message (str): 要发送的消息内容。
        re_chat (bool, 可选): 是否重新开始聊天，默认为False。

        返回:
        ChatInfo: 聊天响应信息。

        抛出:
        GingAIError: 如果请求失败或返回非预期结果。
        """
        url = f"{self.api_base}/application/chat_message/{chat_id}"
        data = {"message": message, "re_chat": re_chat, "stream": False}
        logger.info(f"Sending request to {url} with data: {data}")
        response = self.session.post(url, json=data)
        ging_resp = self._handle_response(response)
        return GingAIChatResponse(ging_resp)


if __name__ == "__main__":
    gingai_client = GingAIClient(
        api_base="http://101.126.146.36:8080/api",
        api_key="application-4fb7c17a8cb94e1ed43e3c81a6ce75da",
        application_id="c3416ea6-e83e-11ef-8666-00163e6fdd1d",
    )
    chat_id = gingai_client.get_chat_id()
    resp = gingai_client.chat(chat_id, "你好")
    print(resp)
