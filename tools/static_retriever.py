from langchain_core.tools import tool
from staticcontext import StaticContextLoader

knowledge_base = StaticContextLoader()

@tool
def consultar_manuais(busca: str) -> str:
    """
    Consulta a base de conhecimento oficial, manuais, escopo do projeto e dados do time da Ouv.ai.
    Use sempre que precisar de informações internas sobre a empresa ou equipe para responder ao usuário.
    """
    return knowledge_base.buscar_contexto(busca)