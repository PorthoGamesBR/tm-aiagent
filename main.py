import os
from dotenv import load_dotenv
from agent import Agent
from agent_state import AgentState
import subprocess
import sys

# from ContextBuilder import ContextBuilder

# Glue to all pieces of the project

"GITHUB_TOKEN", "TRELLO_KEY", "TRELLO_TOKEN" , "TRELLO_BOARD_ID"

CONFIG_PATH = "E:\\Projetos\\ouv.ia\\projectmanageraiagent\\config.json"

load_dotenv()

MOCK_MODE = True

def bootstrap():
    print("[SYSTEM] Iniciando ecossistema Ouv.ai...")
    
    agent = "Esse é um agente mock, feito para ser usado quando está sem tokens restantes para testar"
    
    if not MOCK_MODE:
        # 1. Inicializa o agente com todas as configs de produção
        agent = Agent(
            model=Agent.models.GROQ,
            key=os.getenv("GROQ_KEY"))
    
        
    # 2. Salva a instância pronta no gerenciador de estado
    AgentState.set_agent(agent)
    
    print("[SYSTEM] Agente e RAG carregados com sucesso. Abrindo interface do time...")
    
    # 3. Dispara o Streamlit programaticamente apontando para o arquivo de chat
    # Isso faz o Streamlit rodar no background compartilhando a mesma memória do processo
    subprocess.run([sys.executable, "-m", "streamlit", "run", "interface.py"])

if __name__ == "__main__":
    bootstrap()