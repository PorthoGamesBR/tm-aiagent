from langchain_groq import ChatGroq
from langchain.agents import create_agent


class Agent:
    class models:
        GROQ = "groq"

    def __init__(self, model:models, key:str, system_prompt:str, tools:list):
        self.model = model
        self.api_key = key
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent = self.instantiate_agent()

        
        
    def instantiate_agent(self):
        llm = None
        if self.model == Agent.models.GROQ:
            llm = self.groq()
        else:
            raise NotImplementedError
        
        agent = create_agent(llm, tools=self.tools, system_prompt=self.system_prompt)
        return agent
    
    def groq(self):
        # Initialize Groq LLM
        llm = ChatGroq(
            api_key=self.api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        return llm
    
    def send_message(self, message, message_history = []):
        result = self.agent.invoke(
            {"messages": message_history + [{"role": "user", "content": message}]}
        )
        
        # DEBUG: Remove later
        print(result)
        return result['messages'][-1].content

    
        