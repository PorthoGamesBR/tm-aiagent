from .available_models import Providers, LLMs
from langchain_groq import ChatGroq

class Model:
    def __init__(self, provider: Providers, model: LLMs, api_key: str):
        self.llm = None
        if provider == Providers.GROQ:
            self.llm = Model._groq(api_key, model)
        else:
            raise NotImplementedError
    
    def _groq(api_key, model: LLMs):
        # Initialize Groq LLM
        try:
            llm = ChatGroq(
                api_key=api_key,
                model_name=model,
                temperature=0.3
            )
            return llm
        except Exception as e:
            raise Exception("Erro ao iniciar o modelo Groq: " + e)