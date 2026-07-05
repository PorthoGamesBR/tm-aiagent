from langchain.agents import create_agent
from .model import Model

# NOTE Porto 30/06/2026 23:13 Does this class add anything useful? It seems like a wrapper around langchain
# Awnser: There is something usefull about this class. It minimizes the complexity of langchain into easy to use functions for the rest of the project

# NOTE Porto 04/07/2026 18:55 From now on this class only serves as a base for other agents, like an interface without being one itself (because python
# dont like interfaces).

# NOTE Porto 04/07/2026 19:03 And for instantiating simple agents too.

class Agent:
    
    def __init__(self, model: Model, system_prompt="", tools=[]):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent = self._instantiate_agent()
        
    def _instantiate_agent(self):
        agent = create_agent(self.model.llm, tools=self.tools, system_prompt=self.system_prompt)
        return agent
    
    def send_message(self, message, message_history = []):
        result = self.agent.invoke(
            {"messages": message_history + [{"role": "user", "content": message}]}
        )
        
        # DEBUG: Remove later
        print(result)
        return result['messages'][-1].content

    
        