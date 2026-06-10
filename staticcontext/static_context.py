import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # Ou OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class StaticContextLoader:
    
    def __init__(self):
        # Descobre o caminho absoluto do diretório onde este arquivo está para evitar erros de importação
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = self._construir_base_vetorial()
        
    def _read_file(self, filename):
        """Lê um arquivo markdown de forma segura."""
        file_path = os.path.join(self.base_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de contexto estático não encontrado: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
        
    def _construir_base_vetorial(self):
        textos = [
            self._read_file("BUSINESSINFO.md"),
            self._read_file("PROJECT.md"),
            self._read_file("TEAM.md")
        ]
        
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=100
        )
        
        documentos_fragmentados = text_splitter.create_documents(textos)
        
        return FAISS.from_documents(documentos_fragmentados, self.embeddings)

    def buscar_contexto(self, query: str) -> str:
        # Busca os trechos mais parecidos com a dúvida do usuário
        documentos = self.vector_store.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in documentos])