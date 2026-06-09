import os

class StaticContextLoader:
    def __init__(self):
        # Descobre o caminho absoluto do diretório onde este arquivo está para evitar erros de importação
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
    def _read_file(self, filename):
        """Lê um arquivo markdown de forma segura."""
        file_path = os.path.join(self.base_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de contexto estático não encontrado: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_all_context(self):
        """Retorna o conteúdo de todos os documentos estáticos."""
        return {
            "business_info": self._read_file("BUSINESSINFO.md"),
            "project_info": self._read_file("PROJECT.md"),
            "team_info": self._read_file("TEAM.md")
        }