from .project_context_database import ProjectContextDatabase
from .project_context import ProjectContextData, ProjectTask

class ProjectContextService:

    def __init__(self, database: ProjectContextDatabase):
        self._database = database
        self._current_document : ProjectContextData = self._database.load()
        self._last_doc_version = self._get_current_version()
        if not self._last_doc_version:
            self._current_document = {'objetivo': '', 'tarefas': [], 'pessoas': [], 'decisoes': [], 'riscos': [], 'roadmap': [], 'version': ''}
            
        
    def _get_current_version(self) -> str:
        if self._current_document:
            return self._current_document['version']
        else:
            return None
        
    def _save(self):
        # TODO: Implement Rate Limit
        current_last_doc = self._database.load()
        if current_last_doc:
            self._database.save(current_last_doc, current_last_doc['version'])
        new_version = self._create_version()
        self._current_document['version'] = new_version
        self._database.save(self._current_document, 'current')
        self._last_doc_version = new_version
        
    
    def _create_version(self) -> str:
        int_version = 0
        if self._last_doc_version:
            int_version = int(self._last_doc_version[1:])
        return f'v{int_version+1}'
    
    def add_task(self, titulo: str, descricao: str, prioridade: str, status: str, skills: list[str], dependencias: list[str] = []) -> int:
        tasks = self._current_document.get('tarefas',[])
        if len(tasks) <= 0:
            id = 1
        else:
            id = max(tasks, key=lambda x: x["id"])['id'] + 1
        
        new_task : ProjectTask = {'id':id,
                                  'titulo':titulo, 
                                  'descricao':descricao, 
                                  'prioridade':prioridade, 
                                  'status': status, 
                                  'dependencias':dependencias, 
                                  'skills':skills, 
                                  'responsavel':''}
        tasks.append(new_task)
        self._save()
        return id

    def assign_task(self, task_id: int, nome_responsavel: str, status: str) -> int:
        tasks = self._current_document.get('tarefas',[])
        if len(tasks) <= 0:
            return -1
        task = next((obj for obj in tasks if obj['id'] == task_id), None)
        if not task:
            return -1

        task["responsavel"] = nome_responsavel
        task['status'] = status
        
        developer = self.get_pessoa(nome_responsavel)

        if developer:
            developer["current_tasks_ids"].append(task["id"])

        self._save()
        return task["id"]

    def finish_task(self, task_id: int) -> int:
        tasks = self._current_document.get('tarefas',[])
        if len(tasks) <= 0:
            return -1
        task = next((obj for obj in tasks if obj['id'] == task_id), None)
        if not task:
            return -1
        
        task['status'] = "FINALIZADO"
        self._save()
        return task['id']

    def update_task(self, task_id: int, 
                    titulo: str = None, 
                    descricao: str = None, 
                    prioridade: str = None, 
                    status: str = None, 
                    skills: list[str] = [], 
                    dependencias: list[str] = []) -> int:
        tasks = self._current_document.get('tarefas',[])
        if len(tasks) <= 0:
            return -1
        task = next((obj for obj in tasks if obj['id'] == task_id), None)
        if not task:
            return -1
        
        if titulo:
            task["titulo"] = titulo
        if descricao:
            task['descricao'] = descricao
        if prioridade:
            task['prioridade'] = prioridade
        if status:
            task['status'] = status
        if len(skills) > 0:
            task['skills'] = skills
        if len(dependencias) > 0:
            task['dependencias'] = dependencias
   
        self._save()
        return task['id']
        
    def add_decision(self, decisao: str):
        if decisao not in self._current_document["decisoes"]:
            self._current_document["decisoes"].append(decisao)
            self._save()

    def add_risk(self, risco: str):        
        if risco not in self._current_document["riscos"]:
            self._current_document["riscos"].append(risco)
            self._save()
        
    def update_document(self, doc: ProjectContextData):
        self._current_document = doc
        self._save()

    def get_tarefas(self):
        return self._current_document['tarefas']
    
    def get_pessoas(self):
        return self._current_document['pessoas']
    
    def get_pessoa(self, nome):
        return next((x for x in self.get_pessoas() if x.get('nome','') == nome), None) 
    
    def get_decisoes_feitas(self):
        return self._current_document['decisoes']
    
    def get_riscos(self):
        return self._current_document['riscos']
    
    def get_roadmap(self):
        return self._current_document['roadmap']
    
    def get_roadmap_step(self, step: int = -1):
        roadmap = self.get_roadmap()
        if step == -1:
            return max(roadmap, key=lambda x: x.get('passo',-1))
        else:
            return next((x for x in roadmap if x.get('passo',-1) == step), None) 
        
    def get_project(self) -> ProjectContextData | None:
        return self._current_document
    
    def get_project_markdown(self) -> str:
        doc = self.get_project()
        if doc:
            lines: list[str] = []

            lines.append("# Estado do Projeto")
            lines.append("")
            lines.append(f"**Versão:** {doc['version']}")
            lines.append("")

            # Objetivo
            lines.append("## Objetivo")
            lines.append(doc["objetivo"] or "_Não definido._")
            lines.append("")

            # Roadmap
            lines.append("## Roadmap")

            if doc["roadmap"]:
                for step in sorted(doc["roadmap"], key=lambda s: s["passo"]):
                    lines.append(
                        f"{step['passo']}. **{step['titulo']}**"
                    )

                    if step["descricao"]:
                        lines.append(f"   - {step['descricao']}")
            else:
                lines.append("_Nenhum passo definido._")

            lines.append("")

            # Equipe
            lines.append("## Equipe")

            if doc["pessoas"]:
                for dev in doc["pessoas"]:
                    lines.append(f"### {dev['nome']}")

                    skills = ", ".join(dev["skills"]) if dev["skills"] else "Nenhuma"

                    current = (
                        ", ".join(map(str, dev["current_tasks_ids"]))
                        if dev["current_tasks_ids"]
                        else "Nenhuma"
                    )

                    lines.append(f"- Skills: {skills}")
                    lines.append(f"- Tarefas atuais: {current}")
                    lines.append("")
            else:
                lines.append("_Nenhum colaborador cadastrado._")
                lines.append("")

            # Tarefas
            lines.append("## Tarefas")

            if doc["tarefas"]:
                for task in doc["tarefas"]:
                    lines.append(f"### #{task['id']} - {task['titulo']}")

                    lines.append(f"- Status: {task['status']}")
                    lines.append(f"- Prioridade: {task['prioridade']}")

                    responsavel = task["responsavel"] or "Não atribuído"

                    lines.append(f"- Responsável: {responsavel}")

                    if task["descricao"]:
                        lines.append(f"- Descrição: {task['descricao']}")

                    if task["skills"]:
                        lines.append(
                            "- Skills necessárias: "
                            + ", ".join(task["skills"])
                        )

                    if task["dependencias"]:
                        lines.append(
                            "- Dependências: "
                            + ", ".join(map(str, task["dependencias"]))
                        )

                    lines.append("")
            else:
                lines.append("_Nenhuma tarefa cadastrada._")
                lines.append("")

            # Decisões
            lines.append("## Decisões")

            if doc["decisoes"]:
                for decision in doc["decisoes"]:
                    lines.append(f"- {decision}")
            else:
                lines.append("_Nenhuma decisão registrada._")

            lines.append("")

            # Riscos
            lines.append("## Riscos")

            if doc["riscos"]:
                for risk in doc["riscos"]:
                    lines.append(f"- {risk}")
            else:
                lines.append("_Nenhum risco registrado._")

            lines.append("")

            return "\n".join(lines)
        else:
            return ''