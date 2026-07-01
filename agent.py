from langchain_groq import ChatGroq
from langchain.agents import create_agent

# NOTE Porto 30/06/2026 23:13 Does this class add anything useful? It seems like a wrapper around langchain
# Awnser: There is something usefull about this class. It minimizes the complexity of langchain into easy to use functions for the rest of the project

class Agent:
    class Sources:
        GROQ = "groq"
        
    class Models:
        LLAMA = "llama-3.3-70b-versatile"
    

    def __init__(self, model_source:Sources, key:str, system_prompt:str, tools:list, model_name:Models):
        self.model_source = model_source
        self.model_name = model_name
        self.api_key = key
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent = self.instantiate_agent()

    
        
    def instantiate_agent(self):
        llm_fun = self.llm_source(self.model_source)
        
        agent = create_agent(llm_fun(self.api_key, self.model_name), tools=self.tools, system_prompt=self.system_prompt)
        return agent
    
    def llm_source(self, model_source: Sources):
        llm_source_function = None
        if model_source == Agent.models.GROQ:
            llm_source_function = self.groq
        else:
            raise NotImplementedError
        
        return llm_source_function
    
    def groq(self, api_key, model_name):
        # Initialize Groq LLM
        try:
            llm = ChatGroq(
                api_key=api_key,
                model_name=model_name,
                temperature=0.3
            )
            return llm
        except Exception as e:
            raise Exception("Erro ao iniciar o modelo Groq: " + e)
    
    def send_message(self, message, message_history = []):
        result = self.agent.invoke(
            {"messages": message_history + [{"role": "user", "content": message}]}
        )
        
        # DEBUG: Remove later
        print(result)
        return result['messages'][-1].content

    
        