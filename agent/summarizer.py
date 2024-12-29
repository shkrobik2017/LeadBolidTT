from typing import List

from redis_app.redis_repository import RedisClient


class Summarizer:
    def __init__(self, model):
        self.model = model
        self.prompt = self._load_prompt

    @staticmethod
    async def _load_prompt(redis_client: RedisClient):
        cached_prompt = await redis_client.get_by_key("summarizer_prompt")
        if not cached_prompt:
            with open(f"agent/roles/summarizer.md", "r") as file:
                result = file.read()
                await redis_client.set_key(
                    key="summarizer_prompt",
                    value=result
                )
                return result
        return cached_prompt

    async def summary(self, redis_client: RedisClient, chat_history: List[tuple]):
        prompt = self.prompt(redis_client=redis_client)

        messages = [("system", prompt)]
        messages.extend(chat_history)

        result = await self.model.ainvoke(messages)
        return result.content