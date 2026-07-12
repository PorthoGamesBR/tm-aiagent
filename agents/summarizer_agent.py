from langchain.agents import create_agent
from .model import Model

class SummarizerAgent:
    _SYSTEM_PROMPT = """
    Leia o documento enviado.

    Extraia apenas as informações úteis para compreender um projeto.

    Retorne um resumo em Markdown.
    """
    
    def __init__(self, model: Model, system_prompt="", tools=[], checkpointer=None):
        self.system_prompt = SummarizerAgent._SYSTEM_PROMPT
        self.model = model
        self.agent = self._instantiate_agent()

                
    def _instantiate_agent(self):
        agent = create_agent(self.model.llm, system_prompt=self.system_prompt)
        return agent
    
    def send_message(self, message, message_history = [], thread_id: str = ""): 
        result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]}
            )
        
        return result['messages'][-1].content