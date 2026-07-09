from typing import TypedDict

class ProjectTask(TypedDict):
  id: int
  titulo: str
  descricao: str
  prioridade: str
  status: str
  responsavel: str | None
  dependencias: list
  skills: list[str]

class ProjectDevProfile(TypedDict):
    nome: str
    skills: list[str]
    current_tasks_ids: list[int]
    
class ProjectRoadmapStep(TypedDict):
    passo: int
    titulo: str
    descricao: str
    
class ProjectContextData(TypedDict):
    objetivo: str
    tarefas: list[ProjectTask]
    pessoas: list[ProjectDevProfile]
    decisoes: list[str]
    riscos: list[str]
    roadmap: list[ProjectRoadmapStep]
    version: str