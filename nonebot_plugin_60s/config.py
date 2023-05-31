from typing import Tuple
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    calendar_cookie: str = ""    # 填写微信公众号的cookie
    calendar_token: str = ""   # 填写微信公众号的token
