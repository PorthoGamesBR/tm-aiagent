import os
from dotenv import load_dotenv
from agent import Agent
# from ContextBuilder import ContextBuilder

# Glue to all pieces of the project

"GITHUB_TOKEN", "TRELLO_KEY", "TRELLO_TOKEN" , "TRELLO_BOARD_ID"

CONFIG_PATH = "E:\\Projetos\\ouv.ia\\projectmanageraiagent\\config.json"

load_dotenv()


agent = Agent(
    model=Agent.models.GROQ,
    key=os.getenv("GROQ_KEY")
)

print(agent.send_message("Quais as próximas tarefas que a equipe deve executar?"))