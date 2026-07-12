from .loader import Loader

class GithubLoader(Loader):
    
    def __init__(self):
        self.content = ''
        self.source = ''
        self.title = ''