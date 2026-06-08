from github import Github as PyGithub
from github import Auth

class Github:
    # Criação de um Enum simples para manter compatibilidade com o seu código
    class status:
        OPEN = "open"
        CLOSED = "closed"

    def __init__(self, config_data):
        """
        config_data deve ser um dicionário contendo:
        {
            "token": "seu_github_token",
            "repo": "nome_do_usuario/nome_do_repositorio"
        }
        """
        token = config_data.get("token")
        repo_name = config_data.get("repo")
        
        # Autenticação utilizando o padrão da PyGithub
        auth = Auth.Token(token)
        self.gh = PyGithub(auth=auth)
        self.repo = self.gh.get_repo(repo_name)

    def get_prs(self, status="open"):
        """Busca Pull Requests com base no status."""
        prs = self.repo.get_pulls(state=status)
        
        # Formata os dados para o padrão que o seu ContextBuilder espera
        formatted_prs = []
        for pr in prs:
            formatted_prs.append({
                "title": pr.title,
                "user": {"login": pr.user.login}
            })
        return formatted_prs

    def get_issues(self, assigned=False):
        """Busca issues. Se assigned=False, traz apenas as que não têm dono."""
        # state='open' garante que só pegamos o que está ativo
        issues = self.repo.get_issues(state="open")
        
        formatted_issues = []
        for issue in issues:
            # PyGithub traz PRs junto com Issues. Filtramos para pegar só as Issues puras.
            if issue.pull_request is None:
                # Se queremos apenas as não atribuídas:
                if not assigned and len(issue.assignees) == 0:
                    formatted_issues.append({"title": issue.title})
                elif assigned and len(issue.assignees) > 0:
                    formatted_issues.append({"title": issue.title})
                    
        return formatted_issues

    def get_commits(self, limit=5):
        """Busca os últimos commits da branch principal."""
        commits = self.repo.get_commits()
        
        formatted_commits = []
        for commit in commits[:limit]:
            formatted_commits.append({
                "commit": {
                    "author": {"name": commit.commit.author.name},
                    "message": commit.commit.message
                }
            })
        return formatted_commits