import asyncio
from typing import List
from langchain_core.globals import set_llm_cache
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.cache import RedisCache
from agent.summarizer import Summarizer
from db.db_services import error_handler
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from settings import settings


class MainAgent:
    def __init__(self):
        self.model = ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.BASE_OLLAMA_URL
        ) if settings.LLM_NAME == "ollama" else ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY

        )
        self.prompt_template = self._load_agent_role
        self.summarizer = Summarizer(self.model)

    @staticmethod
    async def _load_agent_role(group_prompt_name: str, redis_client: RedisClient) -> str:
        cached_prompt = await redis_client.get_by_key(f"prompt_file_{group_prompt_name}")
        if not cached_prompt:
            with open(f"agent/roles/{group_prompt_name}.md", "r") as file:
                result = file.read()
                await redis_client.set_key(
                    key=f"prompt_file_{group_prompt_name}",
                    value=result
                )
                return result
        return cached_prompt

    async def check_tokens_count_in_background(
            self,
            redis_client: RedisClient,
            chat_history: List[tuple],
            repo: DBRepository,
            user_id: str
    ):
        logger.info("Start chat history summarizing process.")
        new_summary = await self.summarizer.summary(
            redis_client=redis_client,
            chat_history=chat_history
        )
        await repo.update_messages_status_and_save_summary(
            user_id=user_id,
            summary=new_summary,
            redis_client=redis_client
        )

    @error_handler
    async def generate_response(
            self,
            *,
            content: str,
            chat_history: List[tuple],
            group_prompt_name: str,
            redis_client: RedisClient,
            summary: str
    ) -> BaseMessage:
        logger.info(f"Generating response for {content=} process is started")
        prompt = await self.prompt_template(group_prompt_name=group_prompt_name, redis_client=redis_client)

        messages = [("system", prompt), ("system", summary)]
        messages.extend(chat_history)

        result = await self.model.ainvoke(messages)
        logger.info(f"Response generated successful: {result=}")
        return result
