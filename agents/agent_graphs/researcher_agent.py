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
        area_completed: dict
        completude_score: int
            

    class AnswerEvaluation(BaseModel):
        valid: bool
        reason: str
        
    class ContextEvaluation(BaseModel):
        completed_areas: dict
        completude_score: int

    def __init__(self, model: Model, system_prompt="", tools=[], **kwargs):
        # Sem checkpointer, interrupt() não tem onde persistir o estado entre
        # chamadas — cada .invoke() reiniciaria do zero em vez de retomar de
        # onde parou. MemorySaver serve bem para dev/teste; em produção troque
        # por algo persistente (SqliteSaver, PostgresSaver, etc.).
        self.checkpointer = kwargs.get("checkpointer") or MemorySaver()
        self.config = kwargs.get("config") or {}
        
        # LLMs init
        self.llm = model.llm
        self.answer_llm = self.llm.with_structured_output(ResearcherAgent.AnswerEvaluation, method="json_mode")
        self.structured_llm = self.llm.with_structured_output(ResearcherAgent.ContextEvaluation, method="json_mode")

        graph = StateGraph(ResearcherAgent.ResearchState)

        # Nodes
        graph.add_node("introduction", self._introduction)
        graph.add_node("wait_initial_description", self._wait_initial_description)
        graph.add_node("validate_answer", self._validate_answer)
        graph.add_node("update_context", self._update_context)
        graph.add_node("generate_question", self._generate_question)
        graph.add_node("ask_user", self._ask_user)
        graph.add_node("evaluate_coverage", self._evaluate_coverage)

        # Fluxo inicial: introdução -> descrição inicial -> primeiro documento -> critica -> cobertura
        graph.add_edge(START, "introduction")
        graph.add_edge("introduction", "wait_initial_description")
        graph.add_edge("wait_initial_description", "validate_answer")
        graph.add_conditional_edges("validate_answer", self._should_retry)
        graph.add_edge("update_context", "evaluate_coverage")
        graph.add_conditional_edges("evaluate_coverage", self._should_ask_more)
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
            "area_completed" : {
                        "Empresa": False,
                        "Equipe": False,
                        "Produto": False,
                        "Problema": False,
                        "Usuários": False,
                        "Processos": False,
                        "Tecnologia": False,
                        "Arquitetura": False,
                        "Requisitos": False,
                        "Roadmap": False,
                        "Riscos": False,
                        "Métricas": False,
                        "Projeto Atualmente": False
                        },
            # TODO: Remove this later, find a better way of initializing area_completed
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
            
            Assuntos que ainda precisam ser estudados mais a fundo:
            
            {[k for k,v in state['area_completed'].items() if not v]}

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
        
        IMPORTANTE:
        Sua resposta será consumida por um programa.
        Não escreva análise, justificativa ou markdown.
        Retorne somente os campos solicitados, escrito json na frente.
        Retorne exatamente os seguintes campos:
            valid: bool
            reason: str
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
            Não invente informações, apenas atualize o documento com a resposta mantendo a formatação já existente.
            O documento deve ser como um manual, não deve referenciar a forma que foi feito. Nenhuma formatação ou título deve citar passos de entrevista, como "pergunta" ou "resposta da equipe".
            Não remova informações.
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
        critical_areas = [
            "Produto",
            "Problema",
            "Usuários",
            "Tecnologia",
            "Requisitos",
            "Projeto Atualmente"
        ]
        if state.get('completude_score', 0) < 8 and not all(state['area_completed'][a] for a in critical_areas):
            print(f"DEBUG: Generating another question. Current completude score: {state.get('completude_score', 0)}.")
            return "generate_question"
        print("DEBUG: Not generating more questions, score alreday is 8 or more")
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
    def _evaluate_coverage(self, state: ResearchState):
        prompt = f"""
        Documento:

        {state['context_document']}
        
        Areas:
        
        {state['area_completed']}
        
        Score atual:
        {state.get('completude_score',0)}

        Analise o documento, procure por detalhes que poderiam ser analisados mais profundamentos e duvidas que podem surgir de um gerente de negócios ao ler o documento. Quanto mais informações melhor o score.
        Caso não consiga pensar em nenhuma duvida, marque a área relacionada ao assunto como completa.
        Dê um score de completude para o documento baseado no seguinte:
        1 - Muitas informações faltantes, não é possível um gerente visualizar tudo que precisa sobre cada area do projeto
        5 - Ta ok, mas pode melhorar bastante
        10 - É impossível ter mais detalhes sobre cada area do que o que já tem nesse documento
        
        IMPORTANTE:
        Sua resposta será consumida por um programa.
        Não escreva análise, justificativa ou markdown.
        Retorne somente os campos solicitados, escrito json na frente.
        Retorne exatamente os seguintes campos:
  "completed_areas": dict,
  "completude_score": int
        O score não pode ser menor que o atual
        Não marque areas que já estão como "True" como "False"  
"""
        coverage = self.structured_llm.invoke(prompt)

        area_completed = state['area_completed']
        print(f"DEBUG: Areas completed by the agent: {coverage.completed_areas}")
        for k,v in coverage.completed_areas.items():
            if k in area_completed.keys():
                area_completed[k] = v
        return {
            "area_completed": area_completed,
            "completude_score": coverage.completude_score
        }

    def finalize(self, state: ResearchState):
        return state

    def should_continue(self, state: ResearchState):
        if state["completed"]:
            return END
        return "generate_question"
