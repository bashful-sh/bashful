"""
LLM: Local & Cloud Cache Interface
"""

import time
import json
import redis


class LLMCache:
    local: redis.Redis
    cloud: redis.Redis

    def __init__(
        self,
        local_host="localhost",
        local_port=6379,
        cloud_host=None,
        cloud_port=None,
        cloud_password=None,
        cloud_username=None,
        *args,
        **kwargs,
    ) -> None:
        self.local = redis.Redis(
            host=local_host,
            port=local_port,
            decode_responses=True,
        )
        if cloud_host is not None:
            try:
                self.local.ping()
            except redis.ConnectionError as e:
                self.local.close()
                raise RuntimeError(
                    f"Failed to establish connection with local key/value store: {str(e)}"
                )
            try:
                self.cloud = redis.Redis(
                    host=cloud_host,
                    port=cloud_port,
                    username=cloud_username,
                    password=cloud_password,
                    ssl=True,
                    decode_responses=True,
                )
                try:
                    self.cloud.ping()
                except redis.ConnectionError as e:
                    self.cloud.close()
                    raise RuntimeError(
                        f"Failed to establish connection with cloud key/value store: {str(e)}"
                    )
            except Exception as e:
                self.cloud = None
                print(
                    f"Failed to establish connection with cloud key/value store: {str(e)}"
                )
        else:
            self.cloud = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _set_local(self, key: str, value: dict, ex=None):
        serialized = json.dumps(value)
        return self.local.set(key, serialized, ex=ex)

    def _get_local(self, key: str):
        data = self.local.get(key)
        return json.loads(data) if data else None

    def _set_cloud(self, key: str, value: dict, ex=None):
        serialized = json.dumps(value)
        return self.cloud.set(key, serialized, ex=ex)

    def _get_cloud(self, key: str):
        data = self.cloud.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value_dict: dict, ex=None) -> None:
        value_dict["last_modified"] = time.time()
        self.set_local(key, value_dict, ex)
        if self.cloud is not None:
            self.set_cloud(key, value_dict, ex)

    def get(self, key: str, safe: bool = True) -> dict | None:
        local_data = self.get_local(key)
        if (not safe and local_data is not None) or (self.cloud is None):
            return local_data
        cloud_data = self.get_cloud(key)

        if local_data is None and cloud_data is not None:
            local_data = cloud_data
            self._set_local(key, cloud_data)
        elif cloud_data is None and local_data is not None:
            cloud_data = local_data
            self._set_cloud(key, local_data)

        if local_data["last_modified"] > cloud_data["last_modified"]:
            self.set_cloud(key, local_data)
            return local_data
        return cloud_data

    def close(self) -> None:
        self.local.close()
        if self.cloud is not None:
            self.cloud.close()


cache = LLMCache()
