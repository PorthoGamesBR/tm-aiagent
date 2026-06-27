import json
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.staticfiles import StaticFiles
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
        
    def __init__(self, name):
        self.name = name
        self.status = AgentAcessPoint.AgentStatus.NOT_AVAILABLE
        
    def set_available(self, available=True):
        self.status = AgentAcessPoint.AgentStatus.AVAILABLE
        if not available:
            self.status = AgentAcessPoint.AgentStatus.NOT_AVAILABLE
            
class DocumentDatabase:
    def __init__(self, firestore_client: firestore.Client):
        self.collection = firestore_client.collection('contextdoc')
    
    def get_context_document(self) -> str:
        query = self.collection.limit(1)
        docs = query.stream()
        latest_doc = None
        for doc in docs:
            latest_doc = doc.to_dict()
            break  # We only asked for 1, so we can break immediately
        if not latest_doc:
            return None
        
        return latest_doc['content']
    
    def save_context_document(self, document_text):
        pass
    
    def delete_context_document(self):
        pass
                
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
        
        

settings = Settings()

# Database Configuration
firebase_info = json.loads(settings.firebase_service_account_json)
cred = credentials.Certificate(firebase_info)
firebase_app = firebase_admin.initialize_app(cred)
firestore_client = firestore.client(firebase_app)

doc_db = DocumentDatabase(firestore_client)
user_db = UserDatabase(firestore_client)

# Agent Configuration
researcher_agent = AgentAcessPoint("researcher")
manager_agent = AgentAcessPoint("manager")
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
    
@app.get("/api/contextdoc")
async def contextdoc():
    return {"content": doc_db.get_context_document()}

@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username and form_data.password are automatically available here
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

app.mount("/", StaticFiles(directory="./front", html=True), name="static")