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
        context_document: str | None
        evaluation_reason : str | None
        answered_questions: list
        retry_question: int

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
        graph.add_node("introduction", self._introduction)
        graph.add_node("wait_initial_description", self._wait_initial_description)
        graph.add_node("validate_answer", self._validate_answer)
        graph.add_node("update_context", self._update_context)
        graph.add_node("generate_question", self._generate_question)
        graph.add_node("ask_user", self._ask_user)

        # Fluxo inicial: introdução -> descrição inicial -> primeiro documento -> critica -> cobertura
        graph.add_edge(START, "introduction")
        graph.add_edge("introduction", "wait_initial_description")
        graph.add_edge("wait_initial_description", "validate_answer")
        graph.add_conditional_edges("validate_answer", self._should_retry)
        graph.add_conditional_edges("update_context", self._should_ask_more)
        graph.add_edge("generate_question", "ask_user")
        graph.add_edge("ask_user", "validate_answer")

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
    def _introduction(self, state: ResearchState):
        question = "O que vocês estão tentando construir?"
        message = f"""Olá! Sou o Maestro.\n\nVou ajudar a entender o projeto, a equipe e o contexto atual antes de começarmos a organizar o trabalho.\nPara começar, me conte: {question}"""
        return {
            "assistant_message": message,
            "last_question": question
        }

    def _wait_initial_description(self, state: ResearchState):
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
    def _generate_question(self, state: ResearchState):
        if state.get("valid_answer"):
            prompt = f"""
            Você é um investigador de projetos.

            Documento:

            {state['context_document']}

            Perguntas já respondidas:

            {state['answered_questions']}

            Sua tarefa:

            1. Descubra o assunto mais importante que ainda não foi investigado.
            2. Faça apenas UMA pergunta.
            3. Não gere plano.
            4. Não faça várias perguntas.

            Retorne somente a pergunta.
            """
        else: 
            prompt = f"""
            Você é um investigador de projetos no meio de uma entrevista e acabou de receber uma resposta que foi avaliada da seguinte forma.

            {state ['evaluation_reason']}

            Ultima pergunta:
            
            {state['last_question']}

            Ultima resposta:
            
            {state['last_answer']}

            Sua tarefa:

            1. Crie uma pergunta para enviar ao entrevistado explicando o motivo da sua ultima resposta ter sido reprovada.
            2. Faça apenas UMA pergunta.
            3. Não gere plano.
            4. Não faça várias perguntas.
            5. O objetivo ainda é responder a pergunta original. Não faça uma pergunta que não leve a resposta da pergunta original.

            Retorne somente a pergunta.
            """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        print(f"DEBUG: Question: \n{response.content}")

        return {
            "last_question": response.content
        }

    def _ask_user(self, state: ResearchState):
        answer = interrupt(
            {
                "question": state["last_question"]
            }
        )

        return {
            "last_answer": answer
        }

# ---------------- Validação da resposta ----------------
    def _validate_answer(self, state: ResearchState):
        question = state["last_question"]
        answer = state["last_answer"]

        prompt = f"""
        Pergunta feita ao usuário:

        {question}

        Resposta do usuário:

        {answer}

        Avalie se a resposta realmente responde à pergunta (mesmo que de forma
        breve ou incompleta, mas coerente). Caso o usuário não saiba responder, ou não possa responder, é uma resposta valida. 
        Considere inválida **apenas** se for vazia, se for outra pergunta, sem relação com a pergunta, ou claramente evasiva.  

        Se inválida, explique o motivo.
        """

        evaluation = self.answer_llm.invoke(prompt)

        if evaluation.valid:
            return {"valid_answer": True, "answered_questions": state.get('answered_questions', []) + [question], "retry_question":0}

        # resposta invalida
        print(f"DEBUG: Resposta não válida. Motivo: {evaluation.reason}")
        return {
            "valid_answer": False,
            "evaluation_reason" : evaluation.reason,
            "retry_question": state.get("retry_question", 0) + 1
        }

    def _should_retry(self, state: ResearchState):
        valid_answer = state.get("valid_answer", True)
        retries = state.get("retry_question", 0)
        if valid_answer:
            print("DEBUG: Going to update context")
            return "update_context"
        elif not valid_answer and retries <= 3:
            print("DEBUG: Not updating context, time to ask a new question")
            return "generate_question"
        else:
            # TODO: Change this to a node explaining the motive for the ending of the conversation
            return END

    # ---------------- Atualização de contexto ----------------
    def _update_context(self, state: ResearchState):
        last_question = state["last_question"]
        last_answer = state["last_answer"]

        prompt = f"""
            Você está produzindo um documento que vai ser usado por um gerente de equipe para seu processo decisório diário.
            Ele está sendo produzido durante uma entrevista com a equipe que esse gerente vai assumir.
            O documento deve ser como um manual, não deve referenciar a forma que foi feito.
            Atualize o documento em Markdown.
            Documento atual:

            {state.get('context_document', '')}
            
            Pergunta feita a equipe:
            
            {last_question}

            Resposta da equipe:

            {last_answer}
            """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        print(f"DEBUG: Novo documento: \n{response.content}")

        return {
            "context_document": response.content
        }
        
    def _should_ask_more(self, state: ResearchState):
        if len(state.get('answered_questions', [])) <= 3:
            print(f"DEBUG: Generating another question. Already have {len(state.get('answered_questions', []))} answered questions")
            return "generate_question"
        print("DEBUG: Not generating more question, already have 3")
        return END

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
