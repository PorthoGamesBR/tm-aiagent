from dotenv import dotenv
import os

from agent import Agent
from backend.services.chat_service import ChatService
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_key: str
    jwt_secret: str
    database_provider: str = "firebase"
    firebase_project_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env"
    )


class Application:
    def __init__(self):
        self.settings = Settings()

        self.agent = Agent(
            model=Agent.models.GROQ,
            key=os.getenv("GROQ_KEY")
        )

        self.chat_service = ChatService(
            agent=self.agent
        )