"""
Factory de tools do LangChain para o ProjectContextService.

Por que uma factory e não @tool direto nos métodos da classe?
---------------------------------------------------------------
O decorator @tool inspeciona a assinatura da função para montar o schema
que o LLM preenche. Se ele for aplicado dentro do corpo da classe, o
parâmetro `self` ainda não foi resolvido e:
  1) o LLM passaria a "ver" `self` como um argumento no schema; e
  2) o atributo do método na classe viraria um objeto BaseTool estático,
     quebrando chamadas internas como self.add_task(...) dentro da própria
     classe.

Por isso, a classe de negócio fica intocada e criamos as tools depois,
já com uma instância (bound methods / closures), aqui fora.
"""

from langchain_core.tools import tool

from .project_context_service import ProjectContextService
import json

def build_project_context_tools(service: ProjectContextService) -> list:
    """Recebe uma instância de ProjectContextService e devolve a lista de
    tools prontas para serem passadas a um agent (bind_tools / create_agent)."""

    @tool
    def add_task(
        titulo: str,
        descricao: str,
        prioridade: str,
        status: str,
        skills: list[str],
        dependencias: list[str] = [],
    ) -> int:
        """Cria uma nova tarefa no projeto e retorna o id gerado."""
        return service.add_task(titulo, descricao, prioridade, status, skills, dependencias)

    @tool
    def assign_task(task_id: int, nome_responsavel: str, status: str) -> int:
        """Atribui uma tarefa existente a um responsável, atualizando o status.
        Retorna o id da tarefa ou -1 se não encontrada."""
        return service.assign_task(task_id, nome_responsavel, status)

    @tool
    def finish_task(task_id: int) -> int:
        """Marca uma tarefa como finalizada. Retorna o id da tarefa ou -1 se não encontrada."""
        return service.finish_task(task_id)

    @tool
    def update_task(
        task_id: int,
        titulo: str = None,
        descricao: str = None,
        prioridade: str = None,
        status: str = None,
        skills: list[str] = [],
        dependencias: list[str] = [],
    ) -> int:
        """Atualiza campos de uma tarefa existente. Apenas os campos informados
        são alterados. Retorna o id da tarefa ou -1 se não encontrada."""
        return service.update_task(task_id, titulo, descricao, prioridade, status, skills, dependencias)

    @tool
    def add_decision(decisao: str) -> str:
        """Registra uma nova decisão de projeto (não duplica se já existir)."""
        service.add_decision(decisao)
        return "Decisão registrada."

    @tool
    def add_risk(risco: str) -> str:
        """Registra um novo risco do projeto (não duplica se já existir)."""
        service.add_risk(risco)
        return "Risco registrado."

    @tool
    def get_tarefas() -> str:
        """Retorna a lista completa de tarefas do projeto."""
        tarefas = service.get_tarefas()
        if not tarefas or len(tarefas) <= 0:
            return "Nenhuma tarefa cadastrada no projeto."
        return json.dumps(tarefas, ensure_ascii=False)

    @tool
    def get_pessoas() -> str:
        """Retorna a lista de pessoas/colaboradores do projeto."""
        pessoas = service.get_pessoas()
        if not pessoas or len(pessoas) <= 0:
            return "Nenhuma pessoa cadastrada no projeto."
        return json.dumps(pessoas, ensure_ascii=False)

    @tool
    def get_pessoa(nome: str) -> str:
        """Busca uma pessoa do projeto pelo nome."""
        pessoa = service.get_pessoa(nome)
        if not pessoa:
            return f"Nenhuma pessoa encontrada com o nome '{nome}'."
        return json.dumps(pessoa, ensure_ascii=False)

    @tool
    def get_decisoes_feitas() -> str:
        """Retorna a lista de decisões já registradas no projeto."""
        decisoes = service.get_decisoes_feitas()
        if not decisoes or len(decisoes) <= 0:
            return "Nenhuma decisao cadastrada no projeto."
        return json.dumps(decisoes, ensure_ascii=False)

    @tool
    def get_riscos() -> str:
        """Retorna a lista de riscos registrados no projeto."""
        riscos = service.get_riscos()
        if not riscos or len(riscos) <= 0:
            return "Nenhum risco cadastrado no projeto."
        return json.dumps(riscos, ensure_ascii=False)

    @tool
    def get_roadmap() -> str:
        """Retorna o roadmap completo do projeto."""
        roadmap = service.get_roadmap()
        if not roadmap or len(roadmap) <= 0:
            return "Nenhum roadmap no projeto."
        return json.dumps(roadmap, ensure_ascii=False)

    @tool
    def get_roadmap_step(step: int = -1) -> str:
        """Retorna um passo específico do roadmap. Se step for -1, retorna o
        passo de maior número (o mais avançado)."""
        roadmap_step = service.get_roadmap_step(step)
        if not roadmap_step:
            return f"Nenhum roadmap_step de numero '{step}' encontrado."
        return json.dumps(roadmap_step, ensure_ascii=False)

    @tool
    def get_project_markdown() -> str:
        """Retorna o estado atual do projeto inteiro formatado em Markdown
        (objetivo, roadmap, equipe, tarefas, decisões e riscos)."""
        return service.get_project_markdown()

    return [
        add_task,
        assign_task,
        finish_task,
        update_task,
        add_decision,
        add_risk,
        get_tarefas,
        get_pessoas,
        get_pessoa,
        get_decisoes_feitas,
        get_riscos,
        get_roadmap,
        get_roadmap_step,
        get_project_markdown,
    ]


# Exemplo de uso:
#
# from .project_context_database import ProjectContextDatabase
# from .project_context_service import ProjectContextService
# from .project_context_tools import build_project_context_tools
#
# database = ProjectContextDatabase(...)
# service = ProjectContextService(database)
# tools = build_project_context_tools(service)
#
# llm_with_tools = llm.bind_tools(tools)