from langchain_groq import ChatGroq
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware import MemoryMiddleware

class Agent:
    SYSTEM_PROMPT = """
    Você é o Gerente de Projetos e Operações sênior da Ouv.ai, uma startup de Banking Tech (B2B). 
    Seu estilo de gestão é altamente pragmático, direto ao ponto e focado em eficiência.

    Seu papel é atuar como líder técnico e operacional. Quando o usuário te der uma instrução, use as ferramentas disponíveis para buscar o estado em tempo real dos sistemas (como o Trello) e combine com a base estática acima para ditar os rituais, cobrar o time nominalmente e organizar o fluxo de trabalho.
    
    ⚠️ RECONHECIMENTO DE RESTRIÇÃO DA API (URGENTE):
    Você NÃO tem permissão para usar tags XML como '<function=...' ou disparar chamadas de funções/tools internas de 'write_todos'. 
    Sua resposta deve ser PURAMENTE texto corrido em Markdown direcionado ao usuário humano. 
    Se você tiver ações ou tarefas para a equipe, escreva-as em uma lista de transmissão normal no corpo do seu texto, NUNCA chame a função externa 'write_todos'.
    """
    
    class models:
        GROQ = "groq"

    def __init__(self, model, key):
        self.model = model
        self.api_key = key
        self.backend = StateBackend()
        self.agent = self.instantiate_agent()
        

    def instantiate_agent(self):
        llm = None
        if self.model == Agent.models.GROQ:
            llm = self.groq()
        else:
            raise NotImplementedError
        
        tools = []
        agent = create_deep_agent(
            llm, 
            tools=tools, 
            system_prompt=Agent.SYSTEM_PROMPT,
            backend=self.backend,
            middleware=[
                MemoryMiddleware(
                                backend=self.backend,
                                sources=[
                                    "./staticcontext/TEAM.md",
                                    "./staticcontext/BUSINESSINFO.md",
                                    "./staticcontext/PROJECT.md"
                                ]
                            )
            ]
        )
        return agent
    
    def groq(self):
        # Initialize Groq LLM
        llm = ChatGroq(
            api_key=self.api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.0
        )
        
        return llm
    
    def send_message(self, message):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]}
        )
        
        # DEBUG: Remove later
        print(result)
        return result['messages'][-1].content

    
        