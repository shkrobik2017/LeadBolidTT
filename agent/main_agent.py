from typing import List
from langchain_core.globals import set_llm_cache
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
    async def _load_agent_role(group_name: str, redis_client: RedisClient) -> str:
        cached_prompt = await redis_client.get_by_key(f"prompt_file_{group_name}")
        if not cached_prompt:
            with open(f"agent/roles/{group_name}_agents_role.md", "r") as file:
                result = file.read()
                await redis_client.set_key(
                    key=f"prompt_file_{group_name}",
                    value=result
                )
                return result
        return cached_prompt

    @error_handler
    async def generate_response(
            self,
            *,
            content: str,
            user_id: str,
            chat_history: List[tuple],
            group_name: str,
            redis_client: RedisClient,
            repo: DBRepository,
            summary: str
    ) -> str:
        logger.info(f"Generating response for {content=} process is started")
        prompt = await self.prompt_template(group_name=group_name, redis_client=redis_client)

        messages = [("system", prompt), ("system", summary)]
        messages.extend(chat_history)

        print(messages)

        result = await self.model.ainvoke(messages)
        if result.usage_metadata["input_tokens"] >= 500:
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
        logger.info(f"Response generated successful: {result=}")
        return result.content
