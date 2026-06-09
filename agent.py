from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.agents import create_agent
import json

class Agent:
    class models:
        GROQ = "groq"

    def __init__(self, model, key):
        self.model = model
        self.api_key = key
        self.agent = self.instantiate_agent()
        
    def instantiate_agent(self):
        llm = None
        if self.model == Agent.models.GROQ:
            llm = self.groq()
        else:
            raise NotImplementedError
        
        tools = []
        agent = create_agent(llm, 
                             tools=tools,
                             system_prompt="Você é um gerente de projetos. Deve ser pragmático e focado em resultados.")
        return agent
    
    def groq(self):
        # Initialize Groq LLM
        llm = ChatGroq(
            api_key=self.api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7
        )
        
        return llm

    def send_message(self, message):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]}
        )
        
        return result['messages'][-1].content

    
        