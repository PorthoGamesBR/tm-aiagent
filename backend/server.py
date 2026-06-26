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

class AgentAcessPoint:
    
    class AgentStatus:
        AVAILABLE = "available"
        NOT_AVAILABLE = "not available"
        
    def __init__(self, name):
        self.name = name
        self.status = AgentAcessPoint.AgentStatus.NOT_AVAILABLE
        
    def set_available(self, available=True):
        self.status = AgentAcessPoint.AgentStatus.AVAILABLE
        if not available:
            self.status = AgentAcessPoint.AgentStatus.NOT_AVAILABLE
            
                

settings = Settings()
app = FastAPI()

researcher_agent = AgentAcessPoint("researcher")
manager_agent = AgentAcessPoint("manager")
registered_agent_acess_points = [researcher_agent, manager_agent]

def evaluate_agent_status():
    # If the context document exists, then only the manager should be available. If it doesn't, only the researcher should be available
    context_doc = None
    if not context_doc:
        researcher_agent.set_available()
        manager_agent.set_available(False)
    else:
        researcher_agent.set_available(False)
        manager_agent.set_available()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/agents")
async def agents():
    """Retuns a list of agents and their status"""
    evaluate_agent_status()
    return {
        agent.name: agent.status for agent in registered_agent_acess_points
    }

app.mount("/", StaticFiles(directory="./front", html=True), name="static")