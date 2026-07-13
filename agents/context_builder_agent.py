from langchain.agents import create_agent
from .model import Model

from .summarizer_agent import SummarizerAgent
from backend.context import KnowledgeDocument, Loader
from backend import ProjectContextData
from typing import TypedDict

class ContextBuilderAgent:
    class KnowledgeSummary(TypedDict):
        source: str
        summary: str
    
    def __init__(self, model: Model, system_prompt="", tools=[], checkpointer=None, loaders: list[Loader] = [], summarizer_model: Model = None):
        self.loaders = loaders
        self.model = model
        self.answer_llm = self.model.llm.with_structured_output(ProjectContextData, method="json_mode")
        if not summarizer_model:
            self.summarizer = SummarizerAgent(model)
        else:
            self.summarizer = SummarizerAgent(summarizer_model)
        # self.system_prompt = ''
        # self.agent = self._instantiate_agent()

                
    def _instantiate_agent(self):
        agent = create_agent(self.model.llm, system_prompt=self.system_prompt)
        return agent
    
    def _build_prompt(self) -> str:
        loaded_ctx = [loader.load() for loader in self.loaders]
        kss = []
        for l in loaded_ctx:
            ks : ContextBuilderAgent.KnowledgeSummary = {
                'source' : l['source'],
                'summary': self.summarizer.send_message(l['content'])
            }
            kss.append(ks)
        prompt = f"""
        Você receberá diversos documentos relacionados ao projeto. Esses documentos podem conter informações sobre:

        - produto;
        - negócio;
        - mercado;
        - código fonte;
        - arquitetura;
        - equipe;
        - documentação técnica;
        - roadmap;
        - clientes;
        - requisitos.

        Sua função NÃO é dar sugestões.

        Sua função NÃO é criar tarefas.

        Sua função NÃO é melhorar o projeto.

        Sua única função é identificar fatos presentes na documentação e utilizá-los para construir um retrato fiel do estado atual do projeto.

        Extraia apenas informações que possam ser inferidas da documentação.

        Nunca invente informações.

        Caso alguma informação não exista, utilize listas vazias ou textos vazios.
        
        Liste decisões técnicas ou de produto explicitamente observáveis.

        Considere como decisão:

        - tecnologias utilizadas;
        - arquitetura adotada;
        - integrações existentes;
        - padrões arquiteturais;
        - divisão em agentes;
        - banco de dados escolhido.

        Não invente decisões que não possam ser observadas.
        
        roadmap:

        Preencha SOMENTE se existir uma sequência explícita de etapas.

        Não transforme funcionalidades em roadmap.
        
        objetivo
        → Objetivo do Produto

        decisoes
        → Arquitetura
        → Stack
        → Tecnologias
        → Integrações
        → Banco de Dados
        → Pipeline
        → Frameworks

        roadmap
        → Roadmap
        → Etapas
        → Próximas entregas

        pessoas
        → Equipe
        → Autores
        → Responsáveis

        riscos
        → Limitações
        → Problemas conhecidos
        → Riscos
        → TODO
        
        Documentos:
        {kss}
        
        IMPORTANTE:
        Sua resposta será consumida por um programa.
        Não escreva nenhuma explicação.
        Não utilize Markdown.
        Não utilize comentários.
        Retorne somente os campos solicitados, escrito json na frente.
        O campo tarefas deve conter apenas tarefas explicitamente descritas na documentação.
        Não transforme roadmap em tarefas.
        Não crie tarefas implícitas.
        Retorne exatamente os campos especificados na estrutura enviada:
            ProjectTask:
                id: int
                titulo: str
                descricao: str
                prioridade: str
                status: str
                responsavel: str | None
                dependencias: list
                skills: list[str]

            ProjectDevProfile:
                nome: str
                skills: list[str]
                current_tasks_ids: list[int]
                
            ProjectRoadmapStep:
                passo: int
                titulo: str
                descricao: str
                
            ProjectContextData:
                objetivo: str
                tarefas: list[ProjectTask]
                pessoas: list[ProjectDevProfile]
                decisoes: list[str]
                riscos: list[str]
                roadmap: list[ProjectRoadmapStep]
                version: str
        """
        
        return prompt
            
    def send_message(self, message, message_history = [], thread_id: str = ""): 
        return None
    
    def build_context(self) -> dict:
        prompt = self._build_prompt()
        print(f"DEBUG: {prompt}")
        pcd : ProjectContextData = self.answer_llm.invoke(prompt)
        if 'ProjectContextData' in pcd.keys():
            return pcd['ProjectContextData']
        return pcd