from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"
        frozen = True

    TG_API_ID: str = Field(
        ...,
        description="Your TG api id"
    )

    TG_API_HASH: str = Field(
        ...,
        description="Your TG api hash"
    )

    TG_SESSION_STRING: str = Field(
        ...,
        description="Your TG account session string"
    )

    TG_GROUP_NAME: str = Field(
        ...,
        description="Main TG group username"
    )

    LLM_NAME: str = Field(
        ...,
        description="LLM name you use for response"
    )

    OLLAMA_MODEL: str = Field(
        ...,
        description="Ollama model you choose"
    )

    BASE_OLLAMA_URL: str = Field(
        default="http://ollama:11434",
        description=""
    )

    OPENAI_MODEL: str = Field(
        ...,
        description="OpenAI model you choose"
    )

    OPENAI_API_KEY: str = Field(
        ...,
        description="Your OpenAI api key"
    )

    MONGODB_PASSWORD: str = Field(
        ...,
        description=""
    )

    MONGODB_USER: str = Field(
        ...,
        description=""
    )

    MONGODB_HOST: str = Field(
        ...,
        description=""
    )

    MONGODB_PORT: int = Field(
        ...,
        description=""
    )

    MONGODB_URI: str = Field(
        ...,
        description=""
    )

    MONGODB_PROTOCOL: str = Field(
        ...,
        description=""
    )

    MONGODB_NAME: str = Field(
        ...,
        description=""
    )

    AGENTS_CONVERSATION_DURATION: int = Field(
        default=1200,
        description="Agents conversation job duration"
    )

    FASTAPI_CONTAINER_NAME: str = Field(
        ...,
        description="Name of the FastAPI docker image"
    )

    REDIS_URL: str = Field(
        ...,
        description="Redis URL"
    )


settings = Settings()
