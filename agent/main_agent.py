from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_openai import OpenAI, ChatOpenAI

from settings import settings


class MainAgent:
    def __init__(self):
        self.model = ChatOllama(
            model=settings.OLLAMA_MODEL,
        ) if settings.LLM_NAME == "ollama" else ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY

        )
        self.role_description_file = "agent_role.md"
        self.prompt_template = self._load_agent_role()

    def _load_agent_role(self) -> str:
        with open(f"agent/{self.role_description_file}", "r") as file:
            return file.read()

    async def generate_response(self, content: str):
        try:
            messages = [
                (
                    "system",
                    self.prompt_template
                ),
                (
                    "user",
                    content
                )
            ]
            result = await self.model.ainvoke(messages)
            return result.content
        except Exception as ex:
            raise ex