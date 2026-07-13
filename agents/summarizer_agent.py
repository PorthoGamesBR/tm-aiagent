from langchain.agents import create_agent
from .model import Model

class SummarizerAgent:
    _SYSTEM_PROMPT_V1 = """
        Você receberá documentação.

        Sua função NÃO é criar um resumo curto.

        Sua função é preservar TODA informação relevante para um gerente de projeto.

        Extraia e organize explicitamente:

        - objetivo do produto
        - roadmap
        - decisões arquiteturais
        - riscos
        - membros da equipe (Não coloque modelos de IA como membros da equipe)
        - responsabilidades
        - clientes
        - tecnologias
        - requisitos
        - problemas conhecidos
        - funcionalidades implementadas
        - funcionalidades planejadas

        Nunca descarte essas informações caso existam.
        
        Preserve apenas informações explicitamente presentes na documentação. Não deduza arquitetura, riscos, equipe, clientes ou responsabilidades. Se uma informação não estiver escrita, não a inclua.

        A resposta pode ter até 30000 caracteres.
    """
    
    _SYSTEM_PROMPT_V2 = """
            Você receberá documentação.
    
            Sua função NÃO é criar um resumo curto.
    
            Sua função é preservar TODA informação relevante para um gerente de projeto.
    
            Seu único objetivo é reduzir caracteres.

            Faça isso através de:

            remover redundâncias;
            remover frases de ligação;
            remover exemplos;
            remover introduções;
            remover conclusões;
            transformar parágrafos em listas;
            transformar texto corrido em itens;
            eliminar repetições.

            Não elimine funcionalidades, decisões, arquitetura, equipe, roadmap ou requisitos apenas para reduzir tamanho.

            A saída será utilizada por outro modelo para construir um contexto do projeto.
            
            Preserve apenas informações explicitamente presentes na documentação. Não deduza arquitetura, riscos, equipe, clientes ou responsabilidades. Se uma informação não estiver escrita, não a inclua.
            
            Nunca remova detalhes técnicos associados a tecnologias, arquitetura ou pipeline.
            
            A resposta pode ter até 30000 caracteres.
        """
    
    def __init__(self, model: Model, system_prompt="", tools=[], checkpointer=None):
        self.system_prompt = SummarizerAgent._SYSTEM_PROMPT_V2
        self.model = model
        print(f"DEBUG: Model being used {model.llm.model_name}")
        self.agent = self._instantiate_agent()

                
    def _instantiate_agent(self):
        agent = create_agent(self.model.llm, system_prompt=self.system_prompt)
        return agent
    
    def send_message(self, message, message_history = [], thread_id: str = ""): 
        result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]}
            )
        
        return result['messages'][-1].content