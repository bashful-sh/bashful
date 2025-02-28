"""
LLM: Session Object
"""

import time

from uuid import uuid4
from backend.llm.cache import cache


class LLMSession:
    uuid: str
    user: dict
    model: dict
    logs: dict
    last_modified: float

    def __init__(
        self, user: dict = {}, model: dict = {}, logs: dict = {}, *args, **kwargs
    ) -> None:
        self.uuid = kwargs.get("uuid", str(uuid4()))
        self.user = user
        self.model = model
        self.logs = logs
        self.last_modified = time.time()

        if "uuid" in kwargs:
            self.load()

    def __dict__(self) -> dict:
        return {
            "uuid": self.uuid,
            "user": self.user,
            "model": self.model,
            "logs": self.logs,
            "last_modified": self.last_modified,
        }

    def load(self) -> None:
        cache.get(self.uuid)
        return
