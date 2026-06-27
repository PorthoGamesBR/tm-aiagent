import json
from datetime import datetime, timedelta, timezone
from agent import Agent

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

import firebase_admin
from firebase_admin import credentials, firestore

from jose import JWTError, jwt
from passlib.context import CryptContext


class Settings(BaseSettings):
    groq_key: str
    jwt_secret: str
    encrypt_algorithm: str = "HS256"
    token_expire_minutes: int = 30
    
    database_provider: str = "firebase"
    
    firebase_service_account_json: str
    firebase_project_id: str = None

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
            "messages": [],
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        return doc_ref.id
        
    def get_chat_history(self, chat_id: str) -> list:
        doc_ref = self.collection.document(chat_id)
        doc = doc_ref.get()
        if not doc.exists:
            return []
        return doc.to_dict().get("messages", [])
    
    def save_history(self, chat_id: str, messages: list):
        doc_ref = self.collection.document(chat_id)
        doc_ref.set({
            "messages": messages,
            "updated_at": firestore.SERVER_TIMESTAMP
        }, merge=True)
        return True
    
    def get_chat_id_by_user(self, username: str) -> list:
        docs = self.collection.where("username", "==", username).stream()
        return [doc.id for doc in docs]

settings = Settings()

# Database Configuration
firebase_info = json.loads(settings.firebase_service_account_json)
cred = credentials.Certificate(firebase_info)
firebase_app = firebase_admin.initialize_app(cred)
firestore_client = firestore.client(firebase_app)

doc_db = DocumentDatabase(firestore_client)
user_db = UserDatabase(firestore_client)
chat_db = ChatDatabase(firestore_client)

# Agent Configuration
MODEL = Agent.models.GROQ
researcher_agent = AgentAcessPoint("researcher", Agent(MODEL, settings.groq_key))
manager_agent = AgentAcessPoint("manager", Agent(MODEL, settings.groq_key))
registered_agent_acess_points = [researcher_agent, manager_agent]

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
    if not context_doc:
        researcher_agent.set_available()
        manager_agent.set_available(False)
    else:
        researcher_agent.set_available(False)
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
    return {"content": doc_db.get_context_document()}

@app.post("/api/contextdoc/save")
async def contextdoc_save():
    pass

@app.post("/api/contextdoc/delete")
async def contextdoc_delete():
    pass

@app.get("/api/chats")
async def get_chat_id_from_user(userdata: dict = Depends(get_current_user)):
    username = userdata["user"]
    return {"id_list": chat_db.get_chat_id_by_user(username)}

@app.get("/api/history/{chat_id}")
async def get_chat_history(chat_id: str) -> dict:
    return {"messages": chat_db.get_chat_history(chat_id)}

@app.post("/api/chat/newchat")
async def create_new_chat(userdata: dict = Depends(get_current_user)):
    username = userdata["user"]
    return {"chat_id": chat_db.create_chat_history(username)}


@app.post("/api/chat/{agent_name}/message/{chat_id}")
async def send_agent_message(agent_name: str, chat_id: str, payload: dict, userdata: dict = Depends(get_current_user)):
    # TODO: i want this function to get the username from the actual login, not the request, so i can guarantee is the user itself that is sending the message
    username = userdata["user"]
    agent = None
    for agent_acesspoint in registered_agent_acess_points:
        if agent_acesspoint.name == agent_name:
            if agent_acesspoint.status != AgentAcessPoint.AgentStatus.AVAILABLE:
                return JSONResponse(status_code=401, content={"detail":f"agent {agent_name} not available"})
            agent = agent_acesspoint.agent
            
    if agent == None:
        return JSONResponse(status_code=401, content={"detail":f"Unknow agent {agent_name}"})
        
    chat_history = chat_db.get_chat_history(chat_id)
    formated_message = f"USUARIO: {username} MENSAGEM: { payload['message'] }"
    try:
        response = agent.send_message(formated_message, chat_history)
    except:
        return JSONResponse(status_code=401, content={"detail":"An error occurred while talking to the agent"})
    
    chat_history.append({"role": "user", "content" : payload['message']})
    chat_history.append({"role": "assistant", "content" : response})
    chat_db.save_history(chat_id, chat_history)
    return {"response" : response}
    
app.mount("/", StaticFiles(directory="./front", html=True), name="static")