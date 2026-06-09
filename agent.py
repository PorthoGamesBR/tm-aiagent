from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent
from staticcontext import StaticContextLoader


class Agent:
    BASE_SYSTEM_PROMPT = """
    Você é o Gerente de Projetos e Operações sênior da Ouv.ai, uma startup de Banking Tech (B2B). 
    Seu estilo de gestão é altamente pragmático, direto ao ponto e focado em eficiência.

    Abaixo estão as informações estruturais e estáticas da nossa empresa que você DEVE conhecer e seguir:

    =========================================
    INFORMAÇÕES DE NEGÓCIO:
    {business_info}
    =========================================
    DOCUMENTAÇÃO DO PROJETO E PRODUTO:
    {project_info}
    =========================================
    MATRIZ DA EQUIPE E PERFIS:
    {team_info}
    =========================================

    Seu papel é atuar como líder técnico e operacional. Quando o usuário te der uma instrução, use as ferramentas disponíveis para buscar o estado em tempo real dos sistemas (como o Trello) e combine com a base estática acima para ditar os rituais, cobrar o time nominalmente e organizar o fluxo de trabalho.
    """
    
    class models:
        GROQ = "groq"

    def __init__(self, model, key):
        context_loader = StaticContextLoader()
        self.static_data = context_loader.get_all_context()
        self.model = model
        self.api_key = key
        self.agent = self.instantiate_agent()
        
    def instantiate_agent(self):
        llm = None
        if self.model == Agent.models.GROQ:
            llm = self.groq()
        else:
            raise NotImplementedError
        
        system_prompt_final = Agent.BASE_SYSTEM_PROMPT.format(
            business_info=self.static_data['business_info'],
            project_info=self.static_data['project_info'],
            team_info=self.static_data['team_info']
        )
        
        tools = []
        agent = create_agent(llm, 
                             tools=tools,
                             system_prompt=system_prompt_final)
        return agent
    
    def groq(self):
        # Initialize Groq LLM
        llm = ChatGroq(
            api_key=self.api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.5
        )
        
        return llm
    
    def send_message(self, message):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]}
        )
        
        # DEBUG: Remove later
        print(result)
        return result['messages'][-1].content

    
        