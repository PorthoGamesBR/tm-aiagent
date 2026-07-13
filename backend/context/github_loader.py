from .loader import Loader
from .knowledge_document import KnowledgeDocument
import httpx
import base64
import re
import difflib

class GithubLoader(Loader):
    """
    Loads project knowledge from a GitHub repository.

    Responsibilities:
    - Authenticate with GitHub
    - Query the REST API
    - Download repository metadata
    """

    CONFIG_FILES = {
        "pyproject.toml",
        "requirements.txt",
        "package.json",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env.example",
        ".env.sample",
        "Makefile",
        "deploy.yml"
    }
    
    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "__pycache__",
}
    
    def __init__(self, owner: str, repo: str, token: str, commit_limit: int = 50, excluded_documents: list[str] = []):
        self.owner = owner
        self.repository = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        headers = {
            "Accept": "application/vnd.github+json"
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.client = httpx.Client(
            headers=headers,
            timeout=30,
        )

        self.source = "GitHub"
        self.title = f"{owner}/{repo}"
        self.content = ""
        
        self._repository_tree = None
        self._default_branch = None
        
        self.commit_limit = commit_limit
        self.excluded_documents = excluded_documents
        
 
    def _get(self, endpoint: str, **params) -> dict:
        """
        Performs a GET request to the GitHub REST API.
        Raises an exception if the request fails.
        """

        response = self.client.get(
            f"{self.base_url}{endpoint}",
            params=params
        )

        response.raise_for_status()
        return response.json()
    
    def _get_repository(self) -> dict:
        """
        Returns repository metadata.

        Example:
            {
                "default_branch": "main",
                "description": "...",
                ...
            }
        """

        return self._get("")
    
    def _get_default_branch(self) -> str:
        """
        Returns the repository default branch (main, master, etc).
        """
        if self._default_branch is None:
            repository = self._get_repository()
            self._default_branch = repository["default_branch"]

        return self._default_branch
    
    
    def _get_repository_tree(self) -> list[dict]:
        """
        Returns every file and directory in the repository.

        Each element contains:
            path
            type ("blob" or "tree")
            sha
        """

        if self._repository_tree is None:
            branch = self._get_default_branch()

            response = self._get(
                f"/git/trees/{branch}",
                recursive=1,
            )

            self._repository_tree = response["tree"]

        return self._repository_tree
    
    def _get_markdown_files(self) -> list[str]:
        tree = self._get_repository_tree()

        return [
            item["path"]
            for item in tree
            if item["type"] == "blob"
            and item["path"].lower().endswith(".md")
        ]
        
    def _get_config_files(self) -> list[str]:
        tree = self._get_repository_tree()

        return [
            item["path"]
            for item in tree
            if item["type"] == "blob"
            and item["path"].split("/")[-1] in GithubLoader.CONFIG_FILES
        ]
        
    def _download_file(self, path: str) -> str:
        """
        Downloads a text file from the repository.

        Returns its decoded contents.
        """

        response = self._get(f"/contents/{path}")

        if response["encoding"] != "base64":
            raise RuntimeError(
                f"Unsupported encoding: {response['encoding']}"
            )

        content = base64.b64decode(
            response["content"]
        ).decode("utf-8")

        return content
    
    def _is_ignored(self, path: str) -> bool:

        parts = path.split("/")

        return any(
            part in GithubLoader.IGNORED_DIRECTORIES
            for part in parts
        )
        
    def _get_issues(self,state: str,per_page: int) -> list[dict]:
        """
        Returns GitHub issues, excluding pull requests.
        """

        issues = self._get(
            "/issues",
            state=state,
            sort="updated",
            direction="desc",
            per_page=per_page,
        )

        return [
            issue
            for issue in issues
            if "pull_request" not in issue
        ]

    def _format_issues(self,issues: list[dict]) -> str:

        if not issues:
            return "No issues found."

        sections = []

        for issue in issues:

            labels = ", ".join(
                label["name"]
                for label in issue["labels"]
            )

            body = (issue["body"] or "")[:5000]

            sections.append(
                f"""## #{issue["number"]} - {issue["title"]}

    State: {issue["state"]}

    Author: {issue["user"]["login"]}

    Labels: {labels if labels else "None"}

    Created: {issue["created_at"]}

    Updated: {issue["updated_at"]}

    Description:

    {body}
    """
            )

        return "\n\n---\n\n".join(sections)
    
    def _get_recent_commits(self,per_page: int = 50) -> list[dict]:
        """
        Returns the most recent commits in the repository.
        """

        return self._get(
            "/commits",
            per_page=per_page,
        )
        
    def _get_commit_details(self,sha: str) -> dict:
        """
        Returns detailed information about a commit,
        including statistics and modified files.
        """

        return self._get(
            f"/commits/{sha}"
        )
        
    def _filter_markdown(self, content: str) -> str:
        """
        Removes irrelevant information from markdown files while preserving
        project knowledge.
        """

        # Remove markdown images
        content = re.sub(
            r'!\[[^\]]*\]\([^)]+\)',
            '',
            content
        )

        # Remove HTML img tags
        content = re.sub(
            r'<img[^>]*>',
            '',
            content,
            flags=re.IGNORECASE
        )

        # Remove picture blocks
        content = re.sub(
            r'<picture.*?</picture>',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Collapse excessive blank lines
        content = re.sub(
            r'\n{3,}',
            '\n\n',
            content
        )

        return content.strip()
    
    def _deduplicate_markdown_docs(self, content: str, threshold=0.7) -> str:
        """
        Uses difflib to remove sentences that have too much similarity with each other
        """
        tokens = re.split(r'(\n|\.)', content.lower())
    
        output_parts = []
        unique_sentences = []
        
        # Track the last valid sentence text we are currently evaluating
        current_sentence = ""
        current_sentence_tokens = []

        for token in tokens:
            if token in ('\n', '.'):
                # We reached the end of a sentence segment
                stripped_sentence = current_sentence.strip()
                
                if not stripped_sentence:
                    # Keep empty lines or standalone dots for exact spacing
                    output_parts.extend(current_sentence_tokens)
                    output_parts.append(token)
                else:
                    # Check similarity against previously saved unique sentences
                    is_duplicate = False
                    for existing in unique_sentences:
                        similarity = difflib.SequenceMatcher(None, stripped_sentence, existing).ratio()
                        if similarity >= threshold:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        unique_sentences.append(stripped_sentence)
                        output_parts.extend(current_sentence_tokens)
                        output_parts.append(token)
                    else:
                        # Skip the duplicate sentence, but keep newlines to preserve spacing if desired
                        if token == '\n':
                            output_parts.append('\n')
                
                # Reset for the next sentence
                current_sentence = ""
                current_sentence_tokens = []
            else:
                # Build the sentence string piece by piece
                current_sentence += token
                current_sentence_tokens.append(token)
                
        # Add any remaining trailing text
        if current_sentence_tokens:
            output_parts.extend(current_sentence_tokens)

        return "".join(output_parts)


        
        
        
    def load_project_tree(self) -> str:
        tree = self._get_repository_tree()
        paths = sorted(item["path"] for item in tree)
        return "\n".join(paths)
    
    def load_markdown_docs(self, configs={}) -> str:
        """
        Loads every markdown document found in the repository.
        """
        debug = configs.get('debug', False)
        markdown_files = self._get_markdown_files()
        markdown_files.sort(
            key=lambda p: (
                not p.lower().endswith("readme.md"),
                p
            )
        )
        sections = []

        for path in markdown_files:
            if self._is_ignored(path):
                continue
            
            if any(pattern in path for pattern in self.excluded_documents):
                sections.append(
                            f"# {path}\n\n"
                            f"File ignored but exists in project.\n"
                        )
                continue
    
            try:
                if debug:
                    print(f"DEBUG: {path}")
                    content = self._download_file(path)
                    print(f"DEBUG: Len before filter ({len(content)})")
                    content = self._filter_markdown(content)
                    print(f"DEBUG: Len after filter ({len(content)})")
                else:
                    content = self._filter_markdown(
                        self._download_file(path)
                    )

            except Exception as e:

                sections.append(
                    f"# {path}\n\n"
                    f"Failed to load file:\n"
                    f"{e}"
                )
                continue

            sections.append(
                f"# {path}\n\n{content}"
            )

        return self._deduplicate_markdown_docs("\n\n---\n\n".join(sections))
    
    def load_config_files(self) -> str:
        """
        Loads project configuration files.

        These files help identify the project's
        technology stack and infrastructure.
        """

        config_files = self._get_config_files()

        if not config_files:
            return "No configuration files found."

        sections = []

        for path in sorted(config_files):

            try:
                content = self._download_file(path)

            except Exception as e:

                sections.append(
                    f"# {path}\n\n"
                    f"Failed to load file:\n"
                    f"{e}"
                )

                continue

            sections.append(
                f"# {path}\n\n{content}"
            )

        return "\n\n---\n\n".join(sections)
    
    def load_open_issues(self) -> str:
        return self._format_issues(
            self._get_issues(
                state="open",
                per_page=100
            )
        )
        
    def load_closed_issues(self) -> str:
        """
        Loads the 20 most recently closed issues.
        """

        return self._format_issues(
            self._get_issues(
                state="closed",
                per_page=20
            )
        )
    
    def load_recent_commits(self) -> str:
        """
        Loads the repository's recent commits.
        """

        commits = self._get_recent_commits(per_page=self.commit_limit)

        if not commits:
            return "No recent commits."

        sections = []

        for commit in commits:

            sha = commit["sha"]

            details = self._get_commit_details(sha)

            stats = details.get("stats", {})

            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            total = stats.get("total", additions + deletions)

            files = details.get("files", [])

            modified_files = "\n".join(
                f"- {file['filename']}"
                for file in files[:3]
            )

            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"]
            message = commit["commit"]["message"]

            sections.append(
    f"""## {date}

    Author: {author}

    Message:
    {message}

    Changes:
    +{additions} / -{deletions} ({total} lines)

    Main files:
    {modified_files if modified_files else "No files"}
    """
            )

        return "\n\n---\n\n".join(sections)
    
    def load(self) -> KnowledgeDocument:

        sections = [
            "# Documentation\n\n" + self.load_markdown_docs(),
            "# Project Structure\n\n" + self.load_project_tree(),
            "# Configuration\n\n" + self.load_config_files(),
            "# Open Issues\n\n" + self.load_open_issues(),
            "# Recently Closed Issues\n\n" + self.load_closed_issues(),
            "# Recent Commits\n\n" + self.load_recent_commits(),
        ]
        
        self.content = "\n\n---\n\n".join(sections)

        return super().load()