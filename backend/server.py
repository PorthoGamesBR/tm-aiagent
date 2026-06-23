from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.staticfiles import StaticFiles


class Settings(BaseSettings):
    groq_key: str
    jwt_secret: str
    database_provider: str = "firebase"
    firebase_project_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()
app = FastAPI()

app.mount("/", StaticFiles(directory="../front", html=True), name="static")

@app.get("/health")
async def health():
    return {"status": "ok"}