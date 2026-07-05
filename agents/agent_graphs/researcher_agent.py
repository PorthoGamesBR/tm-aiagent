from typing import TypedDict
from ..model import Model

from langchain_core.messages import HumanMessage
from langgraph.types import interrupt
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from pydantic import BaseModel


class ResearcherAgent:
    class ResearchState(TypedDict):
        assistant_message: str | None
        last_question: str | None
        last_answer: str | None
        valid_answer: bool

    class AnswerEvaluation(BaseModel):
        valid: bool
        reason: str

    def __init__(self, model: Model, system_prompt="", tools=[], **kwargs):
        # Sem checkpointer, interrupt() não tem onde persistir o estado entre
        # chamadas — cada .invoke() reiniciaria do zero em vez de retomar de
        # onde parou. MemorySaver serve bem para dev/teste; em produção troque
        # por algo persistente (SqliteSaver, PostgresSaver, etc.).
        self.checkpointer = kwargs.get("checkpointer") or MemorySaver()
        self.config = kwargs.get("config") or {}
        
        # LLMs init
        self.llm = model.llm
        self.answer_llm = self.llm.with_structured_output(ResearcherAgent.AnswerEvaluation)

        graph = StateGraph(ResearcherAgent.ResearchState)

        # Nodes
        graph.add_node("introduction", self.introduction)
        graph.add_node("wait_initial_description", self.wait_initial_description)
        graph.add_node("validate_answer", self.validate_answer)

        # Fluxo inicial: introdução -> descrição inicial -> primeiro documento -> critica -> cobertura
        graph.add_edge(START, "introduction")
        graph.add_edge("introduction", "wait_initial_description")
        graph.add_edge("wait_initial_description", "validate_answer")

        graph.add_edge("validate_answer", END)

        self.research_graph = graph.compile(checkpointer=self.checkpointer)

# ---------------- SEND MESSAGE FUNCTION ----------------
    def send_message(self, message, message_history = []):
        result = self.research_graph.invoke(
            Command(resume=message), config=self.config
        )
        
        # DEBUG: Remove later
        print(result)
                
        interrupt = result.get("__interrupt__") or None
        
        if interrupt: 
            interrupt_message = interrupt[0].value
            awnser = interrupt_message.get("message") or interrupt_message.get("question")
            return awnser
        else:
            return None
    
# ---------------- Introducao ----------------
    def introduction(self, state: ResearchState):
        question = "O que vocês estão tentando construir?"
        message = f"""Olá! Sou o Maestro.\n\nVou ajudar a entender o projeto, a equipe e o contexto atual antes de começarmos a organizar o trabalho.\nPara começar, me conte: {question}"""
        return {
            "assistant_message": message,
            "last_question": question
        }

    def wait_initial_description(self, state: ResearchState):
        answer = interrupt(
            {
                "type": "initial_description",
                "message": state["assistant_message"],
            }
        )

        return {
            "last_answer": answer,
        }

# ---------------- Loop de perguntas ----------------
    def generate_question(self, state: ResearchState):
        prompt = f"""
        Você é um investigador de projetos.

        Documento:

        {state['context_document']}

        Cobertura atual:

        {state['investigation_coverage']}

        Notas do critico sobre lacunas:

        {state.get('critic_notes', '')}

        Perguntas já respondidas:

        {state['answered_questions']}

        Sua tarefa:

        1. Descubra o assunto mais importante que ainda não foi investigado.
        2. Faça apenas UMA pergunta.
        3. Não gere plano.
        4. Não faça várias perguntas.

        Retorne somente a pergunta.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {
            "open_questions": state["open_questions"] + [response.content],
            "phase": "DISCOVERY",
        }

    def ask_user(self, state: ResearchState):
        answer = interrupt(
            {
                "question": state["open_questions"][-1]
            }
        )

        return {
            "answered_questions": state["answered_questions"] + [answer]
        }

# ---------------- Validação da resposta ----------------
    def validate_answer(self, state: ResearchState):
        question = state["last_question"]
        answer = state["last_answer"]

        prompt = f"""
        Pergunta feita ao usuário:

        {question}

        Resposta do usuário:

        {answer}

        Avalie se a resposta realmente responde à pergunta (mesmo que de forma
        breve ou incompleta, mas coerente). Caso o usuário não saiba responder, ou não possa responder, é uma resposta valida. 
        Considere inválida **apenas** se for vazia, sem relação com a pergunta, ou claramente evasiva.

        Se inválida, explique o motivo.
        """

        evaluation = self.answer_llm.invoke(prompt)

        if evaluation.valid:
            return {"valid_answer": True}

        # resposta invalida
        print(f"DEBUG: Resposta não válida. Motivo: {evaluation.reason}")
        return {
            "answer_valid": False
        }

    def should_retry(self, state: ResearchState):
        if state.get("answer_valid", True):
            return "update_context"
        return "ask_user"

    # ---------------- Atualização de contexto ----------------
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

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {
            "context_document": response.content
        }

    # ---------------- Critico ----------------
    def critic(self, state: ResearchState):
        prompt = f"""
Documento:

{state['context_document']}

Cobertura:

{state['investigation_coverage']}

O documento possui lacunas importantes para que um gerente
de projetos consiga orientar uma equipe?

Liste as lacunas de forma objetiva, em poucas linhas.
Se não houver lacunas relevantes, responda apenas "Nenhuma lacuna relevante".
"""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {
            "critic_notes": response.content
        }

    # ---------------- Cobertura ----------------
    def evaluate_coverage(self, state: ResearchState):
        prompt = f"""
Documento:

{state['context_document']}

Notas do crítico sobre lacunas:

{state.get('critic_notes', '')}

Marque quais áreas
já possuem informações
suficientes.
"""

        coverage = self.structured_llm.invoke(prompt)

        return {
            "investigation_coverage": coverage.model_dump(exclude={"missing_information"}),
            "missing_information": coverage.missing_information,
            "completed": len(coverage.missing_information) == 0,
        }

    def finalize(self, state: ResearchState):
        return state

    def should_continue(self, state: ResearchState):
        if state["completed"]:
            return END
        return "generate_question"
