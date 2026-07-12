# Base class for all context loaders
from .knowledge_document import KnowledgeDocument

class Loader:
    def load(self) -> KnowledgeDocument:
        doc : KnowledgeDocument = {'content':self.content, 'source':self.source, 'title': self.title}
        return doc