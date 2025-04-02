import json
from dataclasses import dataclass

import redis


@dataclass
class CacheClient:
    client: redis.Redis

    def set_matrix(self, key: str, matrix: list[list[int]]) -> None:
        self.client.set(key, json.dumps(matrix))

    def get_matrix(self, key: str) -> list[list[int]] | None:
        result = self.client.get(key)
        if result:
            return json.loads(result)
        return result
