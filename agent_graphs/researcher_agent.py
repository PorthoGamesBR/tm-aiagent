from typing import TypedDict
from agent import Agent

from langchain_core.messages import HumanMessage
from langgraph.types import interrupt
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from pydantic import BaseModel

class ResearcherAgent:
    class ResearchState(TypedDict):
        context_document: str
        investigation_coverage: dict[str, bool]
        open_questions: list[str]
        answered_questions: list[str]
        assumptions: list[str]
        completed: bool
        
    class Coverage(BaseModel):
        produto: bool
        usuarios: bool
        negocio: bool
        equipe: bool
        stack: bool
        processo: bool
        riscos: bool
        restricoes: bool
    
    INITIAL_STATE = {
        "context_document": "",
        "investigation_coverage": {
            "produto": False,
            "usuarios": False,
            "negocio": False,
            "equipe": False,
            "stack": False,
            "processo": False,
            "riscos": False,
            "restricoes": False,
        },
        "open_questions": [],
        "answered_questions": [],
        "assumptions": [],
        "completed": False,
    }

    def __init__(self, key:str, source: Agent.Sources, model: Agent.Models):
        self.llm = Agent.llm_source(source)(key, model)
        self.structured_llm = (self.llm.with_structured_output(ResearcherAgent.Coverage))
        graph = StateGraph(ResearcherAgent.ResearchState)
        graph.add_node(
            "generate_question",
            self.generate_question
        )
        graph.add_node(
            "ask_user",
            self.ask_user
        )
        graph.add_node(
            "update_context",
            self.update_context
        )
        graph.add_node(
            "evaluate_coverage",
            self.evaluate_coverage
        )
        graph.add_node(
            "finalize",
            self.finalize
        )
        
        graph.add_edge(
            START,
            "generate_question"
        )

        graph.add_edge(
            "generate_question",
            "ask_user"
        )

        graph.add_edge(
            "ask_user",
            "update_context"
        )

        graph.add_edge(
            "update_context",
            "evaluate_coverage"
        )

        graph.add_conditional_edges(
            "evaluate_coverage",
            self.should_continue,
            {
                "generate_question":
                    "generate_question",
                END:
                    "finalize",
            }
        )

        graph.add_edge(
            "finalize",
            END
        )
        self.research_graph = (graph.compile())
        
        
    def generate_question(self, state: ResearchState):
        prompt = f"""
    Você é um investigador de projetos.

    Documento:

    {state['context_document']}

    Cobertura atual:

    {state['investigation_coverage']}

    Perguntas já respondidas:

    {state['answered_questions']}

    Sua tarefa:

    1. Descubra o assunto mais importante que ainda não foi investigado.
    2. Faça apenas UMA pergunta.
    3. Não gere plano.
    4. Não faça várias perguntas.

    Retorne somente a pergunta.
    """

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            "open_questions": [
                response.content
            ]
        }
        
        
        
    # ---------------- Interrupt para perguntar pro usuario ----------------    
    def ask_user(state: ResearchState):
        answer = interrupt(
            {
                "question":
                    state["open_questions"][-1]
            }
        )

        return {
            "answered_questions":
                state["answered_questions"]
                + [answer]
        }
        
    def update_context(self, state: ResearchState):
        answer = state["answered_questions"][-1]

        prompt = f"""
    Documento atual:

    {state['context_document']}

    Nova informação:

    {answer}

    Atualize o documento
    em Markdown.
    """

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            "context_document":
                response.content
        }
        
    def evaluate_coverage(self, state: ResearchState):
        prompt = f"""
    Documento:

    {state['context_document']}

    Marque quais áreas
    já possuem informações
    suficientes.
    """

        coverage = (
            self.structured_llm.invoke(
                prompt
            )
        )

        completed = all(
            coverage.model_dump()
            .values()
        )

        return {
            "investigation_coverage":
                coverage.model_dump(),
            "completed":
                completed
        }
    
    
    def finalize(state: ResearchState):
        return state
    
    def should_continue(state: ResearchState):
        if state["completed"]:
            return END

        return "generate_question"