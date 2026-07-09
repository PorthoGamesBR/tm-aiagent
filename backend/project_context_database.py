from .project_context import ProjectContextData, ProjectTask, ProjectDevProfile, ProjectRoadmapStep

import firebase_admin
from firebase_admin import credentials, firestore

class ProjectContextDatabase:
    def __init__(self, firestore_client):
        # Database Configuration
        self.collection = firestore_client.collection('contextdoc')

    def save(self, project_context: ProjectContextData, doc_version: str = "current"):
        doc_ref = self.collection.document(doc_version)
        doc_ref.set(project_context)
        return True
    
    def load(self, doc_version: str = "current") -> ProjectContextData:
        doc_ref = self.collection.document(doc_version)
        doc = doc_ref.get()
        if not doc.exists:
           return None
        return ProjectContextDatabase._dict_to_project_context_data(doc.to_dict())
    
    def doc_list(self) -> list[str]:
        # list of name of documents on the collection. Each name is a version
        # Efficiently fetch only the document references without downloading full data
        doc_names = [doc.id for doc in self.collection.select([]).stream()]
        return doc_names
    
    def _dict_to_project_roadmap_step(data) -> dict:
        prs : ProjectRoadmapStep = {
            'passo': data.get('passo',-1),
            'titulo': data.get('titulo',''),
            'descricao': data.get('descricao','')
        }
        return prs
    
    def _dict_to_project_dev_profile(data) -> dict:
        pdp : ProjectDevProfile = {
            'nome': data.get('nome',''),
            'skills': data.get('skills',[]),
            'current_tasks_ids': data.get('current_tasks_ids',[])
        }
        return pdp
    
    def _dict_to_project_task(data) -> dict:
        pt : ProjectTask = {
            'id': data.get('id',0),
            'titulo': data.get('titulo',''),
            'descricao': data.get('descricao',''),
            'prioridade': data.get('prioridade',''),
            'status': data.get('status',''),
            'responsavel': data.get('responsavel',''),
            'dependencias': data.get('dependencias',''),
            'skills': [s for s in data.get('skills',[])]
        }
        return pt
        
    def _dict_to_project_context_data(data) -> dict:
        pcd : ProjectContextData = {
            'objetivo': data.get('objetivo', ''),
            'tarefas': [ProjectContextDatabase._dict_to_project_context_data(d) for d in data.get('tarefas',[])],
            'pessoas': [ProjectContextDatabase._dict_to_project_dev_profile(d) for d in data.get('pessoas',[])],
            'decisoes': [s for s in data.get('decisoes',[])],
            'riscos': [s for s in data.get('riscos',[])],
            'roadmap': [ProjectContextDatabase._dict_to_project_roadmap_step(d) for d in data.get('roadmap',[])],
            'version': data.get('version')
        }
        return pcd