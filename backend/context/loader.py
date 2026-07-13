# Base class for all context loaders
from .knowledge_document import KnowledgeDocument

class Loader:
    def load(self) -> KnowledgeDocument:
        if not hasattr(self, "source"):
            raise ValueError("Loader must define 'source'.")

        if not hasattr(self, "title"):
            raise ValueError("Loader must define 'title'.")

        if not hasattr(self, "content"):
            raise ValueError("Loader must define 'content'.")
        
        doc : KnowledgeDocument = {'content':self.content, 'source':self.source, 'title': self.title}
        return doc