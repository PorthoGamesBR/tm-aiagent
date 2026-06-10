from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools import consultar_manuais


class Agent:
    _PERSONA = """
        Você é o Gerente de Projetos e Operações sênior da Ouv.ai, uma startup de Banking Tech (B2B). 
        Seu estilo de gestão é altamente pragmático, direto ao ponto e focado em eficiência.
        Seu papel é analisar o contexto do negócio e do time e ditar o ritmo das operações.
        """
    
    _SYSTEM_PROMPT_TEMPLATE = """
        {persona}
        
        Instruções operacionais:
        - Se a mensagem do usuário for apenas uma dúvida, responda diretamente de forma analítica e estratégica.
        - Se a mensagem demandar uma ação no mundo real, use as ferramentas disponíveis para consultar ou alterar o estado dos sistemas (como o Trello).
        """
        
        
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
        
        
        system_prompt_final = Agent._SYSTEM_PROMPT_TEMPLATE.format(
            persona = Agent._PERSONA
        )
        
        tools = [consultar_manuais]
        agent = create_agent(llm, tools=tools, system_prompt=system_prompt_final)
        return agent
    
    def groq(self):
        # Initialize Groq LLM
        llm = ChatGroq(
            api_key=self.api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        return llm
    
    def send_message(self, message):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]}
        )
        
        # DEBUG: Remove later
        print(result)
        return result['messages'][-1].content

    
        