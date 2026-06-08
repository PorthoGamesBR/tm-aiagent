import os
import requests
from datetime import datetime
import json
from ouvai.org_tools import Trello, Github

class ContextBuilder:
    def __init__(self, config_path):
        # Static configurations
        CONFIGS = json.load(open(config_path, "r"))
        self.github_repo = CONFIGS.get("github_repo")
        
        # Dynamic configurations
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.trello_key = os.getenv("TRELLO_KEY")
        self.trello_token = os.getenv("TRELLO_TOKEN")
        self.trello_board_id = os.getenv("TRELLO_BOARD_ID")
        
        TRELLO_CONFIG_DATA = None
        self.trello = Trello(TRELLO_CONFIG_DATA)
        
        GITHUB_CONFIG_DATA = None
        self.github = Github(GITHUB_CONFIG_DATA)


    def get_github_status(self):
        """Extrai métricas de ritmo de código e gargalos do GitHub."""
        # 1. Buscar Pull Requests abertos (gargalos de code review)
        prs = self.github.get_prs(status=Github.status.OPEN)
        
        # 2. Buscar últimas Issues sem atribuição (tarefas perdidas)
        # assigned_to with empty list returns any issues that has no one assigned to
        issues = self.github.get_issues(assigned=False)
        
        # 3. Analisar últimos commits para ver quem está ativo
        commits = self.github.get_commits()
        
        return {
            "open_prs": [ {"title": pr["title"], "author": pr["user"]["login"]} for pr in prs ],
            "unassigned_issues": [ issue["title"] for issue in issues if "pull_request" not in issue ],
            "recent_commits": [ {"author": c["commit"]["author"]["name"], "message": c["commit"]["message"]} for c in commits ]
        }

    def get_trello_status(self):
        """Extrai o estado das colunas do Trello (Impedidos e Atrasados)."""
        
        # Exemplo simplificado de busca de cards travados
        blocked_cards = self.trello.get_cards(status=Trello.status.BLOCKED)
        overdue_cards = self.trello.get_cards(status=Trello.status.OVERDUE)
        
        # Aqui você filtraria os cards que estão na lista "Impedido" ou sem movimentação
        return {
            "blocked_cards": blocked_cards,
            "overdue_cards": overdue_cards
        }

    def get_static_governance(self):
        """Dados corporativos que não mudam via API automática ainda."""
        
        return {
            "cnpj": "Não emitido",
            "contrato_social": "Pendente de definição de equity",
            "lista_de_espera_leads": 23 # Pode vir de uma API do Stripe/Typeform/Landing Page
        }

    def build_final_context(self):
        gh = self.get_github_status()
        trello = self.get_trello_status()
        gov = self.get_static_governance()
        
# O Payload que vai para a IA agora é focado em GESTÃO E RISCO
        context_prompt = f"""
=========================================
RELATÓRIO DE SAÚDE OPERACIONAL - OUV.AI
=========================================

1. OBJETIVOS DE NEGÓCIO & GOVERNANÇA:
   - Empresa Formalizada (CNPJ): {gov['cnpj']}
   - Contrato Social / Equity: {gov['contrato_social']}
   - Funil Comercial: {gov['lista_de_espera_leads']} leads aguardando na Lista de Espera.

2. SAÚDE DA EQUIPE & RITMO DE DESENVOLVIMENTO:
   - Atividade Recente no Código: O repositório recebeu {len(gh['recent_commits'])} commits recentemente.
   - Centralização: Últimos commits efetuados por {[c['author'] for c in gh['recent_commits']]}.

3. GARGALOS E FLUXO DE TRABALHO (PROCESSOS):
   - Pull Requests Pendentes de Revisão (Code Review): {len(gh['open_prs'])} abertos.
     * Detalhes dos PRs: {[pr['title'] for pr in gh['open_prs']]}
   - Cards Travados/Impedidos no Trello: {trello['blocked_cards']}
   - Demandas Técnicas sem Responsável (Tarefas Órfãs): {gh['unassigned_issues']}

Analise os dados acima como o Gerente de Operações da Ouv.ai. Seu papel é cruzar esses indicadores para criar o plano estratégico, definir os rituais necessários (reuniões ou revisões) e cobrar os membros do time para resolver os desequilíbrios apontados.
=========================================
"""
        return context_prompt