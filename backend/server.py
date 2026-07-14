import json
from datetime import datetime, timedelta, timezone
from agents.agent import Agent
from agents.model import Model
from agents import Providers, LLMs, ContextBuilderAgent
from agents.checkpointers import FirestoreCheckpointSaver

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

import firebase_admin
from firebase_admin import credentials, firestore

from jose import JWTError, jwt
from passlib.context import CryptContext

from langchain_core.tools import tool
from groq import RateLimitError, APIError

from .project_context_database import ProjectContextDatabase
from .project_context_service import ProjectContextService
from .context import GithubLoader
from .project_context_service_tools import build_project_context_tools

class Settings(BaseSettings):
    groq_key: str
    jwt_secret: str
    firebase_service_account_json: str
    firebase_project_id: str = None
    encrypt_algorithm: str = "HS256"
    token_expire_minutes: int = 30
    database_provider: str = "firebase"
    github_user: str
    github_repo: str
    github_api_token: str
    github_ignored_files: str = ''
    
    model_config = SettingsConfigDict(
        env_file=".env"
    )
    
    @field_validator("firebase_service_account_json")
    @classmethod
    def validate_json(cls, v: str) -> str:
        try:
            json.loads(v)
            return v
        except ValueError:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON must be a valid JSON string")

class AgentAcessPoint:
    
    class AgentStatus:
        AVAILABLE = "available"
        NOT_AVAILABLE = "not available"
        
    def __init__(self, name, agent):
        self.name = name
        self.status = AgentAcessPoint.AgentStatus.NOT_AVAILABLE
        self.agent = agent
        
    def set_available(self, available=True):
        self.status = AgentAcessPoint.AgentStatus.AVAILABLE
        if not available:
            self.status = AgentAcessPoint.AgentStatus.NOT_AVAILABLE
            
class DocumentDatabase:
    def __init__(self, firestore_client: firestore.Client):
        self.collection = firestore_client.collection('contextdoc')
        self._doc_id = "current"
    
    def get_context_document(self) -> str:
        doc_ref = self.collection.document(self._doc_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        return doc.to_dict().get("content")
    
    def save_context_document(self, document_text):
        doc_ref = self.collection.document(self._doc_id)
        doc_ref.set({
            "content": document_text,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        return True
    
    def delete_context_document(self):
        doc_ref = self.collection.document(self._doc_id)
        doc_ref.delete()
        return True
                
class UserDatabase:
    def __init__(self, firestore_client: firestore.Client):
        self.collection = firestore_client.collection('users')
            
        
    def get_user(self, username) -> dict:
        docs = self.collection.where("username", "==", username).limit(1).stream()
        user = None
        for doc in docs:
            user = doc.to_dict()
            break
        return user
        
class ChatDatabase:
    def __init__(self, firestore_client: firestore.Client):
        # chat_id = unique, every single chat has an id
        # user = inside the chat document itself. Can be used for filters
        self.collection = firestore_client.collection('chats')
            
    def create_chat_history(self, username: str) -> str:
        """Returns the chat_id of the newly created chat file"""
        doc_ref = self.collection.document()
        doc_ref.set({
            "username": username,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        return doc_ref.id
    
    def get_chat_id_by_user(self, username: str) -> list:
        docs = self.collection.where("username", "==", username).stream()
        return [doc.id for doc in docs]
    
class ContextDocPayload(BaseModel):
    content: str
    
# Tools for the agent
@tool
def save_context_doc_tool(document_text: str) -> str:
    """
    Salva o documento de contexto que o agente gerente vai utilizar após.
    """
    if not document_text or not document_text.strip():
        return "Context text is empty. Nothing saved."
    doc_db.save_context_document(document_text.strip())
    return "Context document saved."

@tool
def read_context_doc_tool() -> str:
    """
    Retorna o documento de contexto com o cenário atual da empresa, equipe e tarefas
    """
    content = doc_db.get_context_document()
    return content or "No context document is available."

settings = Settings()

# Database Configuration
firebase_info = json.loads(settings.firebase_service_account_json)
cred = credentials.Certificate(firebase_info)
firebase_app = firebase_admin.initialize_app(cred)
firestore_client = firestore.client(firebase_app)

doc_db = DocumentDatabase(firestore_client)
user_db = UserDatabase(firestore_client)
chat_db = ChatDatabase(firestore_client)

proj_ctx_db = ProjectContextDatabase(firestore_client)
proj_ctx_srv = ProjectContextService(proj_ctx_db)

# Configures the context if it does not exist
context = proj_ctx_db.load()

if context is None:
    cba_model = Model(Providers.GROQ, model=LLMs.LLAMA, api_key=settings.groq_key)
    summary_model = Model(Providers.GROQ, model=LLMs.LLAMA_INSTRUCT, api_key=settings.groq_key, temperature=0.0)
    loaders = [
        GithubLoader(owner=settings.github_user, repo=settings.github_repo, token=settings.github_api_token,commit_limit=5, excluded_documents=settings.github_ignored_files.split(','))
    ]
    cba = ContextBuilderAgent(cba_model, loaders=loaders, summarizer_model=summary_model)
    context = cba.build_context()
    proj_ctx_srv.update_document(context)
                            
# Agent Configuration
SOURCE = Providers.GROQ
MODEL = LLMs.LLAMA
RESEARCHER_PROMPT = ""
MANAGER_PROMPT = ""
with open("chat_agent/prompts/maestroresearcher.md", encoding="utf-8") as file:
    RESEARCHER_PROMPT = file.read()
with open("chat_agent/prompts/maestromanager.md", encoding="utf-8") as file:
    MANAGER_PROMPT = file.read()
    
# researcher_agent = AgentAcessPoint("researcher", Agent(SOURCE, settings.groq_key, RESEARCHER_PROMPT, [save_context_doc_tool], MODEL)
manager_model = Model(SOURCE, MODEL, settings.groq_key)
manager_agent = AgentAcessPoint("manager", Agent(manager_model, 
                                                 f"{MANAGER_PROMPT} \n # Contexto Atual: \n {proj_ctx_srv.get_project_markdown()}",
                                                 checkpointer=FirestoreCheckpointSaver(firestore_client=firestore_client),
                                                 tools=build_project_context_tools(proj_ctx_srv)))

registered_agent_acess_points = [manager_agent]

# Access Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

app = FastAPI()

    
# UTILS
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    to_encode.update({"exp": expire})
    # python-jose syntax is identical here
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.encrypt_algorithm)
    return encoded_jwt

def verify_password(password, hashed_password) -> bool:
    return pwd_context.verify(password, hashed_password)
    
def authenticate_user(username, password) -> dict:
    user_dict = user_db.get_user(username)
    # Authenticate: Check if user exists and password matches
    if not user_dict or not verify_password(password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    return user_dict    

def evaluate_agent_status():
    # If the context document exists, then only the manager should be available. If it doesn't, only the researcher should be available
    context_doc = doc_db.get_context_document()
    researcher_agent = next((x for x in registered_agent_acess_points if x.name == 'researcher'), None)
    manager_agent = next((x for x in registered_agent_acess_points if x.name == 'manager'), None)
    
    if not context_doc:
        if researcher_agent:
            researcher_agent.set_available()
        if manager_agent:
            manager_agent.set_available(False)
    else:
        if researcher_agent:
            researcher_agent.set_available(False)
        if manager_agent:
            manager_agent.set_available()
    
    # DEBUG: Forcing to see if it works. Remove later
    manager_agent.set_available()

def get_token_from_request(request: Request) -> str:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()

# Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if (request.url.path == "/api/login") or (not request.url.path.startswith("/api")):
        return await call_next(request)

    token = get_token_from_request(request)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
    
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.encrypt_algorithm])
        request.state.current_user = payload.get("sub")
        request.state.user_payload = payload
        return await call_next(request)
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

# Endpoints
@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username and form_data.password are automatically available here
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/user")
async def get_current_user(request: Request):
    return {"user": request.state.current_user}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/agents")
async def agents():
    """Retuns a list of agents and their status"""
    evaluate_agent_status()
    return {
        agent.name: agent.status for agent in registered_agent_acess_points
    }
    
@app.get("/api/contextdoc")
async def contextdoc():
    # TODO: Turn this into a tool for the manager model to use
    return {"content": doc_db.get_context_document()}

@app.post("/api/contextdoc/save")
async def contextdoc_save(payload: ContextDocPayload):
    if not payload.content or not payload.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Context content is required")
    doc_db.save_context_document(payload.content.strip())
    return {"status": "ok", "message": "Context document saved"}

@app.post("/api/contextdoc/delete")
async def contextdoc_delete():
    doc_db.delete_context_document()
    return {"status": "ok", "message": "Context document deleted"}

@app.get("/api/chats")
async def get_chat_id_from_user(userdata: dict = Depends(get_current_user)):
    username = userdata["user"]
    return {"id_list": chat_db.get_chat_id_by_user(username)}

@app.get("/api/history/{chat_id}")
async def get_chat_history(chat_id: str, userdata: dict = Depends(get_current_user)) -> dict:
    username = userdata["user"]
    if chat_id not in chat_db.get_chat_id_by_user(username):
        return JSONResponse(status_code=403, content={"detail": "chat does not belong to user"})
    
    # TODO: Make this dynamic to not access manager agent directly
    agent = manager_agent.agent.agent  # o CompiledStateGraph dentro da sua classe Agent
    config = {"configurable": {"thread_id": chat_id}}

    try:
        state = agent.get_state(config)
        if not state.values:
                return {"messages": []}
    except ValueError:
        return {"messages": []}
    
    messages = state.values.get("messages", [])
    return {"messages": [_serialize_message(m) for m in messages]}

def _serialize_message(message) -> dict:
    # Mapeia o "type" do LangChain (human/ai/tool/system) pro formato
    # {"role", "content"} que seu front já espera hoje
    role_map = {"human": "user", "ai": "assistant", "tool": "tool", "system": "system"}
    msg = {
        "role": role_map.get(message.type, message.type),
        "content": message.content,
    }
    if msg['role'] == 'user':
        msg['content'] = msg['content'].split("MENSAGEM: ")[-1]
    return msg

@app.post("/api/chat/newchat")
async def create_new_chat(userdata: dict = Depends(get_current_user)):
    username = userdata["user"]
    return {"chat_id": chat_db.create_chat_history(username)}


@app.post("/api/chat/{agent_name}/message/{chat_id}")
async def send_agent_message(agent_name: str, chat_id: str, payload: dict, userdata: dict = Depends(get_current_user)):
    evaluate_agent_status()
    username = userdata["user"]
    agent = None
    for agent_acesspoint in registered_agent_acess_points:
        if agent_acesspoint.name == agent_name:
            if agent_acesspoint.status != AgentAcessPoint.AgentStatus.AVAILABLE:
                return JSONResponse(status_code=404, content={"detail":f"agent {agent_name} not available"})
            agent = agent_acesspoint.agent
            
    if agent == None:
        return JSONResponse(status_code=500, content={"detail":f"Unknow agent {agent_name}"})
    
    if chat_id not in chat_db.get_chat_id_by_user(username):
        return JSONResponse(status_code=403, content={"detail": "chat does not belong to user"})
    
    formated_message = f"USUARIO: {username} MENSAGEM: { payload['message'] }"
    try:
        response = agent.send_message(formated_message, thread_id=chat_id)
    except RateLimitError as exc:
        return JSONResponse(
            status_code=200,
            content={"response": str(exc), "detail": "Rate limit exceeded"}
        )
    except APIError as exc:
        return JSONResponse(
            status_code=200,
            content={"response": str(exc), "detail": "Error while communicating with Groq API"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )
    
    return {"response" : response}
    
app.mount("/", StaticFiles(directory="./front", html=True), name="static")